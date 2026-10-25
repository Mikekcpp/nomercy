import re

from core.models import Claim, FinalAnswer


class SynthesisAgent:
    """
    Синтез + проверка каждого утверждения по источнику.
    """

    CLAIM_SPLIT = re.compile(r"(?<=[.!?])\s+")

    def __init__(self, llm_call):
        self.llm = llm_call

    def synthesize(self, query: str, context: list[dict]) -> str:
        ctx_block = "\n".join(
            f"[{c['id']}] {c.get('text', '')}" for c in context
        )
        prompt = (
            "Ответь на вопрос ТОЛЬКО по фрагментам ниже. "
            "После каждого утверждения укажи [id] источника.\n\n"
            f"Вопрос: {query}\n\nФрагменты:\n{ctx_block}\n\nОтвет:"
        )
        return self.llm(prompt)

    def extract_claims(self, answer: str,
                       context: list[dict]) -> list[Claim]:
        sentences = [s.strip() for s in self.CLAIM_SPLIT.split(answer) if s.strip()]
        ids = {c["id"] for c in context}

        claims = []
        for s in sentences:
            match = re.search(r"\[(\d+)\]", s)
            src = int(match.group(1)) if match else None
            claims.append(Claim(text=s, source_id=src if src in ids else None))
        return claims

    def verify_claim(self, claim: Claim, context: list[dict]) -> bool:
        if claim.source_id is None:
            return False
        src = next((c for c in context if c["id"] == claim.source_id), None)
        if not src:
            return False

        claim_words = set(re.findall(r"\w{4,}", claim.text.lower()))
        src_words = set(re.findall(r"\w{4,}", src.get("text", "").lower()))
        if not claim_words:
            return False
        overlap = len(claim_words & src_words) / len(claim_words)
        return overlap >= 0.5

    def detect_contradictions(self, context: list[dict]) -> list[str]:
        contradictions = []
        values = {}
        for c in context:
            for key in ("event_time", "status", "location"):
                if key in c:
                    values.setdefault(key, set()).add(str(c[key]))
        for key, vals in values.items():
            if len(vals) > 1:
                contradictions.append(f"Противоречие по '{key}': {sorted(vals)}")
        return contradictions

    def run(self, query: str, context: list[dict]) -> FinalAnswer:
        draft = self.synthesize(query, context)
        claims = self.extract_claims(draft, context)

        for c in claims:
            c.supported = self.verify_claim(c, context)

        uncertainties = [c.text for c in claims if not c.supported]
        contradictions = self.detect_contradictions(context)

        return FinalAnswer(
            summary=draft,
            claims=claims,
            contradictions=contradictions,
            uncertainties=uncertainties,
            grounded=all(c.supported for c in claims) if claims else False,
        )
