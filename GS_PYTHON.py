from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class Profile:
    name: str
    competencies: Dict[str, float] = field(default_factory=dict)
    interests: List[str] = field(default_factory=list)

    def set_competency(self, key: str, score: float):
        self.competencies[key.lower()] = max(0.0, min(10.0, score))

    def get_score(self, key: str) -> float:
        return self.competencies.get(key.lower(), 0.0)


@dataclass
class Career:
    name: str
    competency_weights: Dict[str, float] = field(default_factory=dict)
    description: str = ""
    suggested_learning: List[str] = field(default_factory=list)

    def required_competencies(self) -> List[str]:
        return list(self.competency_weights.keys())


class Recommender:
    def __init__(self, careers: List[Career]):
        self.careers = careers

    def score_profile_for_career(self, profile: Profile, career: Career) -> float:
        total_weight = sum(career.competency_weights.values())
        if total_weight == 0:
            return 0.0
        weighted_sum = 0.0
        for comp, weight in career.competency_weights.items():
            prof_score = profile.get_score(comp)
            weighted_sum += (prof_score / 10.0) * weight
        normalized = (weighted_sum / total_weight) * 100.0
        return round(normalized, 2)

    def recommend(self, profile: Profile, top_n: int = 3, min_score: float = 20.0) -> List[Tuple[Career, float]]:
        scored = []
        for career in self.careers:
            s = self.score_profile_for_career(profile, career)
            interest_bonus = 0.0
            for it in profile.interests:
                if it.lower() in career.name.lower():
                    interest_bonus = 5.0
            s = min(100.0, s + interest_bonus)
            if s >= min_score:
                scored.append((career, s))
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_n]

    def improvement_areas(self, profile: Profile, career: Career, top_k: int = 3) -> List[Tuple[str, float]]:
        gaps = []
        for comp, weight in career.competency_weights.items():
            prof_score = profile.get_score(comp)
            ideal = 8.0
            gap = max(0.0, ideal - prof_score) / 10.0 * 100.0
            importance_gap = gap * weight
            gaps.append((comp, round(importance_gap, 2)))
        gaps.sort(key=lambda x: x[1], reverse=True)
        return gaps[:top_k]


def example_data():
    careers = [
        Career(
            name="Engenheiro de Software",
            competency_weights={
                "lógica": 0.2,
                "programação": 0.25,
                "algoritmos": 0.15,
                "trabalho em equipe": 0.1,
                "comunicação": 0.1,
                "criatividade": 0.05,
                "resolução de problemas": 0.15,
            },
            description="Desenvolve software, resolve problemas e trabalha em times ágeis.",
            suggested_learning=[
                "Estruturas de dados e algoritmos",
                "Práticas de testes (TDD)",
                "Git e fluxo de trabalho colaborativo",
            ],
        ),
        Career(
            name="Cientista de Dados",
            competency_weights={
                "estatística": 0.25,
                "programação": 0.2,
                "machine learning": 0.25,
                "lógica": 0.1,
                "comunicação": 0.1,
            },
            description="Extrai insights de dados e constrói modelos preditivos.",
            suggested_learning=[
                "Aprendizado de máquina",
                "Estatística aplicada",
                "Processamento e limpeza de dados",
            ],
        ),
        Career(
            name="Product Manager",
            competency_weights={
                "comunicação": 0.25,
                "visão de produto": 0.25,
                "colaboração": 0.2,
                "análise de dados": 0.15,
                "criatividade": 0.15,
            },
            description="Conduz visão do produto e coordena times multidisciplinares.",
            suggested_learning=[
                "Estratégia de produto",
                "Design thinking",
                "Métricas e KPIs",
            ],
        ),
        Career(
            name="Designer UX/UI",
            competency_weights={
                "criatividade": 0.3,
                "comunicação": 0.15,
                "prototipagem": 0.2,
                "teste com usuários": 0.15,
            },
            description="Projeta experiências e interfaces centradas no usuário.",
            suggested_learning=[
                "Ferramentas de prototipagem (Figma, Sketch)",
                "Pesquisa com usuários",
                "Princípios de usabilidade",
            ],
        ),
    ]
    return careers


def cli():
    careers = example_data()
    recommender = Recommender(careers)

    print("=== Sistema de Recomendação de Carreira (exemplo) ===")
    name = input("Nome do perfil: ").strip() or "Test User"

    sample_competencies = sorted({
        comp for c in careers for comp in c.competency_weights.keys()
    })

    profile = Profile(name=name)
    print("\nInforme sua nota para as competências (0-10). Aperte enter para 0.")
    for comp in sample_competencies:
        while True:
            try:
                ans = input(f"  {comp.capitalize()}: ").strip()
                if ans == "":
                    score = 0.0
                else:
                    score = float(ans.replace(",", "."))
                profile.set_competency(comp, score)
                break
            except ValueError:
                print("Valor inválido. Informe um número entre 0 e 10.")

    interests = input("\nQuais áreas têm interesse? (separe por vírgula, opcional): ").strip()
    if interests:
        profile.interests = [s.strip() for s in interests.split(",") if s.strip()]

    print("\nGerando recomendações...\n")
    recs = recommender.recommend(profile, top_n=3, min_score=20.0)
    if not recs:
        print("Nenhuma carreira atingiu a pontuação mínima. Considere fortalecer suas competências.")
        return

    for i, (career, score) in enumerate(recs, start=1):
        print(f"{i}. {career.name} — Score: {score}%")
        print(f"   Descrição: {career.description}")
        print("   Trilhas sugeridas:")
        for t in career.suggested_learning:
            print(f"     - {t}")

        gaps = recommender.improvement_areas(profile, career, top_k=3)
        if gaps:
            print("   Áreas para melhorar(prioridade):")
            for comp, gap in gaps:
                prof_val = profile.get_score(comp)
                print(f"     - {comp.capitalize()}: atual {prof_val}/10 — prioridade {gap:.1f}")
        print()

    print("Dica: pratique projetos reais e monte um portfólio para demonstrar suas competências.")
    print("Fim.")


if __name__ == "__main__":
    cli()