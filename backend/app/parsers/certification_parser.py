CERTIFICATION_KEYWORDS = [
    "certification",
    "certificate",
    "coursera",
    "udemy",
    "nptel",
    "aws",
    "microsoft",
    "google",
]


def extract_certifications(text: str):
    certifications = []

    for line in text.splitlines():
        line = line.strip()

        if any(keyword in line.lower() for keyword in CERTIFICATION_KEYWORDS):
            certifications.append(line)

    return list(dict.fromkeys(certifications))