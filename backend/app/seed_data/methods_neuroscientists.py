from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SeedExpertProfile:
    full_name: str
    email: str
    orcid_id: str
    expertise_entries: tuple[str, ...]
    source_url: str


METHODS_NEUROSCIENTIST_EXPERTS: tuple[SeedExpertProfile, ...] = (
    SeedExpertProfile(
        full_name="Russell Poldrack",
        email="russell.poldrack@seeded-experts.dev",
        orcid_id="0000-0001-6755-0259",
        expertise_entries=(
            "Cognitive neuroscience methods",
            "Neuroimaging reproducibility",
            "Open datasets and computational psychiatry",
        ),
        source_url="https://orcid.org/0000-0001-6755-0259",
    ),
    SeedExpertProfile(
        full_name="Yaroslav Halchenko",
        email="yaroslav.halchenko@seeded-experts.dev",
        orcid_id="0000-0003-3456-2493",
        expertise_entries=(
            "Neuroinformatics infrastructure",
            "Reproducible data management",
            "BIDS and data workflow automation",
        ),
        source_url="https://orcid.org/0000-0003-3456-2493",
    ),
    SeedExpertProfile(
        full_name="Ariel Rokem",
        email="ariel.rokem@seeded-experts.dev",
        orcid_id="0000-0003-0679-1985",
        expertise_entries=(
            "Diffusion MRI analysis",
            "Open-source neuroscience software",
            "Research computing education",
        ),
        source_url="https://orcid.org/0000-0003-0679-1985",
    ),
    SeedExpertProfile(
        full_name="Jean-Baptiste Poline",
        email="jean-baptiste.poline@seeded-experts.dev",
        orcid_id="0000-0002-9794-749X",
        expertise_entries=(
            "Neuroimaging statistics",
            "Data sharing and FAIR neuroscience",
            "fMRI methods",
        ),
        source_url="https://orcid.org/0000-0002-9794-749X",
    ),
    SeedExpertProfile(
        full_name="Tal Yarkoni",
        email="tal.yarkoni@seeded-experts.dev",
        orcid_id="0000-0002-6558-5113",
        expertise_entries=(
            "Meta-science",
            "Statistical learning for neuroimaging",
            "Open science methods",
        ),
        source_url="https://orcid.org/0000-0002-6558-5113",
    ),
    SeedExpertProfile(
        full_name="Arno Klein",
        email="arno.klein@seeded-experts.dev",
        orcid_id="0000-0002-0707-2889",
        expertise_entries=(
            "Brain image registration",
            "Neuroimaging data standards",
            "Atlas building and segmentation",
        ),
        source_url="https://orcid.org/0000-0002-0707-2889",
    ),
    SeedExpertProfile(
        full_name="Olaf Sporns",
        email="olaf.sporns@seeded-experts.dev",
        orcid_id="0000-0001-7265-4036",
        expertise_entries=(
            "Connectomics",
            "Network neuroscience",
            "Brain graph analysis",
        ),
        source_url="https://orcid.org/0000-0001-7265-4036",
    ),
    SeedExpertProfile(
        full_name="Tor Wager",
        email="tor.wager@seeded-experts.dev",
        orcid_id="0000-0002-1936-5574",
        expertise_entries=(
            "Affective neuroscience methods",
            "Multivariate fMRI analysis",
            "Pain neuroimaging",
        ),
        source_url="https://orcid.org/0000-0002-1936-5574",
    ),
    SeedExpertProfile(
        full_name="Vince Calhoun",
        email="vince.calhoun@seeded-experts.dev",
        orcid_id="0000-0001-9058-0747",
        expertise_entries=(
            "Computational psychiatry",
            "Functional connectivity",
            "Machine learning for brain imaging",
        ),
        source_url="https://orcid.org/0000-0001-9058-0747",
    ),
    SeedExpertProfile(
        full_name="Michael Breakspear",
        email="michael.breakspear@seeded-experts.dev",
        orcid_id="0000-0003-4943-3969",
        expertise_entries=(
            "Computational neuroscience",
            "Whole-brain dynamics",
            "Neural systems modeling",
        ),
        source_url="https://orcid.org/0000-0003-4943-3969",
    ),
    SeedExpertProfile(
        full_name="Bertrand Thirion",
        email="bertrand.thirion@seeded-experts.dev",
        orcid_id="0000-0001-5018-7895",
        expertise_entries=(
            "Machine learning for neuroimaging",
            "Statistical pattern analysis",
            "Open neuroimaging tools",
        ),
        source_url="https://orcid.org/0000-0001-5018-7895",
    ),
    SeedExpertProfile(
        full_name="Jonathan Peelle",
        email="jonathan.peelle@seeded-experts.dev",
        orcid_id="0000-0001-9194-854X",
        expertise_entries=(
            "Speech and hearing neuroscience",
            "Aging and cognition methods",
            "MRI experiment design",
        ),
        source_url="https://orcid.org/0000-0001-9194-854X",
    ),
    SeedExpertProfile(
        full_name="Stefan Kiebel",
        email="stefan.kiebel@seeded-experts.dev",
        orcid_id="0000-0002-5052-1117",
        expertise_entries=(
            "Dynamic causal modeling",
            "Bayesian neuroimaging",
            "EEG and MEG methods",
        ),
        source_url="https://orcid.org/0000-0002-5052-1117",
    ),
    SeedExpertProfile(
        full_name="Tristan Glatard",
        email="tristan.glatard@seeded-experts.dev",
        orcid_id="0000-0003-2620-5883",
        expertise_entries=(
            "Reproducible neuroimaging pipelines",
            "Scientific workflow systems",
            "Open infrastructure for brain imaging",
        ),
        source_url="https://orcid.org/0000-0003-2620-5883",
    ),
    SeedExpertProfile(
        full_name="Karl Friston",
        email="karl.friston@seeded-experts.dev",
        orcid_id="0000-0001-7984-8909",
        expertise_entries=(
            "Computational neuroimaging",
            "Dynamic causal modeling",
            "Bayesian brain theory",
        ),
        source_url="https://orcid.org/0000-0001-7984-8909",
    ),
    SeedExpertProfile(
        full_name="Peter Bandettini",
        email="peter.bandettini@seeded-experts.dev",
        orcid_id="0000-0001-9038-4746",
        expertise_entries=(
            "fMRI methodology",
            "Ultra-high-field MRI",
            "Brain imaging experiment design",
        ),
        source_url="https://orcid.org/0000-0001-9038-4746",
    ),
    SeedExpertProfile(
        full_name="Kamil Ugurbil",
        email="kamil.ugurbil@seeded-experts.dev",
        orcid_id="0000-0002-8475-9334",
        expertise_entries=(
            "High-field MRI systems",
            "Human Connectome imaging methods",
            "MR instrumentation",
        ),
        source_url="https://orcid.org/0000-0002-8475-9334",
    ),
    SeedExpertProfile(
        full_name="Olaf Hauk",
        email="olaf.hauk@seeded-experts.dev",
        orcid_id="0000-0003-0817-6054",
        expertise_entries=(
            "MEG analysis",
            "Language neuroscience methods",
            "Multimodal brain imaging",
        ),
        source_url="https://orcid.org/0000-0003-0817-6054",
    ),
    SeedExpertProfile(
        full_name="Susan Bookheimer",
        email="susan.bookheimer@seeded-experts.dev",
        orcid_id="0000-0002-3417-5891",
        expertise_entries=(
            "Clinical neuroimaging",
            "Cognitive aging methods",
            "Large-scale MRI studies",
        ),
        source_url="https://orcid.org/0000-0002-3417-5891",
    ),
    SeedExpertProfile(
        full_name="Martin Lindquist",
        email="martin.lindquist@seeded-experts.dev",
        orcid_id="0000-0003-2289-0828",
        expertise_entries=(
            "Neuroimaging statistics",
            "fMRI preprocessing and inference",
            "Time-series methods for brain data",
        ),
        source_url="https://orcid.org/0000-0003-2289-0828",
    ),
)
