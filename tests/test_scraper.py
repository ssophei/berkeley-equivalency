from scraper import scrape_url
import pytest



@pytest.fixture
def return_json_for_de_anze_to_berk_aero():
    return {
        "receivingInstitution": "University of California, Berkeley",
        "sendingInstitution": "De Anza College",
        "type": "Articulation Agreement",
        "articulations": [
            {
            "receiving": {
                "type": "course",
                "subject": "MATH",
                "number": "1A",
                "title": "Calculus",
                "units": 4.0
            },
            "sending": {
                "type": "CourseGroup",
                "courseConjunction": "Or",
                "items": [
                {
                    "type": "CourseGroup",
                    "courseConjunction": "And",
                    "items": [
                    {
                        "type": "course",
                        "subject": "MATH",
                        "number": "1A",
                        "title": "Calculus I",
                        "units": 5.0
                    },
                    {
                        "type": "course",
                        "subject": "MATH",
                        "number": "1B",
                        "title": "Calculus II",
                        "units": 5.0
                    }
                    ]
                },
                {
                    "type": "CourseGroup",
                    "courseConjunction": "And",
                    "items": [
                    {
                        "type": "course",
                        "subject": "MATH",
                        "number": "1AH",
                        "title": "Calculus I - HONORS",
                        "units": 5.0
                    },
                    {
                        "type": "course",
                        "subject": "MATH",
                        "number": "1BH",
                        "title": "Calculus II - HONORS",
                        "units": 5.0
                    }
                    ]
                }
                ]
            }
            },
            {
            "receiving": {
                "type": "course",
                "subject": "MATH",
                "number": "1B",
                "title": "Calculus",
                "units": 4.0
            },
            "sending": {
                "type": "CourseGroup",
                "courseConjunction": "Or",
                "items": [
                {
                    "type": "CourseGroup",
                    "courseConjunction": "And",
                    "items": [
                    {
                        "type": "course",
                        "subject": "MATH",
                        "number": "1B",
                        "title": "Calculus II",
                        "units": 5.0
                    },
                    {
                        "type": "course",
                        "subject": "MATH",
                        "number": "1C",
                        "title": "Calculus III",
                        "units": 5.0
                    }
                    ]
                },
                {
                    "type": "CourseGroup",
                    "courseConjunction": "And",
                    "items": [
                    {
                        "type": "course",
                        "subject": "MATH",
                        "number": "1BH",
                        "title": "Calculus II - HONORS",
                        "units": 5.0
                    },
                    {
                        "type": "course",
                        "subject": "MATH",
                        "number": "1CH",
                        "title": "Calculus III - HONORS",
                        "units": 5.0
                    }
                    ]
                }
                ]
            }
            },
            {
            "receiving": {
                "type": "course",
                "subject": "MATH",
                "number": "53",
                "title": "Multivariable Calculus",
                "units": 4.0
            },
            "sending": {
                "type": "CourseGroup",
                "courseConjunction": "Or",
                "items": [
                {
                    "type": "CourseGroup",
                    "courseConjunction": "And",
                    "items": [
                    {
                        "type": "course",
                        "subject": "MATH",
                        "number": "1C",
                        "title": "Calculus III",
                        "units": 5.0
                    },
                    {
                        "type": "course",
                        "subject": "MATH",
                        "number": "1D",
                        "title": "Calculus IV",
                        "units": 5.0
                    }
                    ]
                },
                {
                    "type": "CourseGroup",
                    "courseConjunction": "And",
                    "items": [
                    {
                        "type": "course",
                        "subject": "MATH",
                        "number": "1CH",
                        "title": "Calculus III - HONORS",
                        "units": 5.0
                    },
                    {
                        "type": "course",
                        "subject": "MATH",
                        "number": "1DH",
                        "title": "Calculus IV - HONORS",
                        "units": 5.0
                    }
                    ]
                }
                ]
            }
            },
            {
            "receiving": {
                "type": "course",
                "subject": "MATH",
                "number": "54",
                "title": "Linear Algebra and Differential Equations",
                "units": 4.0
            },
            "sending": {
                "type": "CourseGroup",
                "courseConjunction": "Or",
                "items": [
                {
                    "type": "CourseGroup",
                    "courseConjunction": "And",
                    "items": [
                    {
                        "type": "course",
                        "subject": "MATH",
                        "number": "2A",
                        "title": "Differential Equations",
                        "units": 5.0
                    },
                    {
                        "type": "course",
                        "subject": "MATH",
                        "number": "2B",
                        "title": "Linear Algebra",
                        "units": 5.0
                    }
                    ]
                },
                {
                    "type": "CourseGroup",
                    "courseConjunction": "And",
                    "items": [
                    {
                        "type": "course",
                        "subject": "MATH",
                        "number": "2AH",
                        "title": "Differential Equations - HONORS",
                        "units": 5.0
                    },
                    {
                        "type": "course",
                        "subject": "MATH",
                        "number": "2BH",
                        "title": "Linear Algebra - HONORS",
                        "units": 5.0
                    }
                    ]
                }
                ]
            }
            },
            {
            "receiving": {
                "type": "course",
                "subject": "PHYSICS",
                "number": "7A",
                "title": "Physics for Scientists and Engineers",
                "units": 4.0
            },
            "sending": {
                "type": "course",
                "subject": "PHYS",
                "number": "4A",
                "title": "Physics for Scientists and Engineers: Mechanics",
                "units": 6.0
            }
            },
            {
            "receiving": {
                "type": "course",
                "subject": "PHYSICS",
                "number": "7B",
                "title": "Physics for Scientists and Engineers",
                "units": 4.0
            },
            "sending": {
                "type": "CourseGroup",
                "courseConjunction": "And",
                "items": [
                {
                    "type": "course",
                    "subject": "PHYS",
                    "number": "4B",
                    "title": "Physics for Scientists and Engineers: Electricity and Magnetism",
                    "units": 6.0
                },
                {
                    "type": "course",
                    "subject": "PHYS",
                    "number": "4C",
                    "title": "Physics for Scientists and Engineers: Fluids, Waves, Optics and Thermodynamics",
                    "units": 6.0
                }
                ]
            }
            },
            {
            "receiving": {
                "type": "course",
                "subject": "ENGLISH",
                "number": "R1A",
                "title": "Reading and Composition",
                "units": 4.0
            },
            "sending": {
                "type": "course",
                "subject": "EWRT",
                "number": "1A",
                "title": "Composition and Reading",
                "units": 5.0
            }
            },
            {
            "receiving": {
                "type": "course",
                "subject": "ENGLISH",
                "number": "R1B",
                "title": "Reading and Composition",
                "units": 4.0
            },
            "sending": {
                "type": "course",
                "subject": "EWRT",
                "number": "1B",
                "title": "Reading, Writing and Research",
                "units": 5.0
            }
            },
            {
            "receiving": {
                "type": "course",
                "subject": "ASTRON",
                "number": "7A",
                "title": "Introduction to Astrophysics",
                "units": 4.0
            },
            "sending": {
                "type": "NotArticulated"
            }
            },
            {
            "receiving": {
                "type": "course",
                "subject": "ASTRON",
                "number": "10",
                "title": "Introduction to General Astronomy",
                "units": 4.0
            },
            "sending": {
                "type": "course",
                "subject": "ASTR",
                "number": "10",
                "title": "Stellar Astronomy",
                "units": 5.0
            }
            },
            {
            "receiving": {
                "type": "CourseGroup",
                "courseConjunction": "And",
                "items": [
                {
                    "type": "course",
                    "subject": "BIOLOGY",
                    "number": "1A",
                    "title": "General Biology Lecture (Cells, Genetics, Animal Form & Function)",
                    "units": 3.0
                },
                {
                    "type": "course",
                    "subject": "BIOLOGY",
                    "number": "1AL",
                    "title": "General Biology Laboratory",
                    "units": 2.0
                }
                ]
            },
            "sending": {
                "type": "CourseGroup",
                "courseConjunction": "Or",
                "items": [
                {
                    "type": "CourseGroup",
                    "courseConjunction": "And",
                    "items": [
                    {
                        "type": "course",
                        "subject": "BIOL",
                        "number": "6A",
                        "title": "Form and Function in the Biological World",
                        "units": 6.0
                    },
                    {
                        "type": "course",
                        "subject": "BIOL",
                        "number": "6B",
                        "title": "Cell and Molecular Biology",
                        "units": 6.0
                    }
                    ]
                },
                {
                    "type": "CourseGroup",
                    "courseConjunction": "And",
                    "items": [
                    {
                        "type": "course",
                        "subject": "BIOL",
                        "number": "6AH",
                        "title": "Form and Function in the Biological World - HONORS",
                        "units": 6.0
                    },
                    {
                        "type": "course",
                        "subject": "BIOL",
                        "number": "6B",
                        "title": "Cell and Molecular Biology",
                        "units": 6.0
                    }
                    ]
                }
                ]
            }
            },
            {
            "receiving": {
                "type": "course",
                "subject": "BIOLOGY",
                "number": "1B",
                "title": "General Biology (Plant Form & Function, Ecology, Evolution)",
                "units": 4.0
            },
            "sending": {
                "type": "CourseGroup",
                "courseConjunction": "Or",
                "items": [
                {
                    "type": "CourseGroup",
                    "courseConjunction": "And",
                    "items": [
                    {
                        "type": "course",
                        "subject": "BIOL",
                        "number": "6A",
                        "title": "Form and Function in the Biological World",
                        "units": 6.0
                    },
                    {
                        "type": "course",
                        "subject": "BIOL",
                        "number": "6C",
                        "title": "Ecology and Evolution",
                        "units": 6.0
                    }
                    ]
                },
                {
                    "type": "CourseGroup",
                    "courseConjunction": "And",
                    "items": [
                    {
                        "type": "course",
                        "subject": "BIOL",
                        "number": "6AH",
                        "title": "Form and Function in the Biological World - HONORS",
                        "units": 6.0
                    },
                    {
                        "type": "course",
                        "subject": "BIOL",
                        "number": "6C",
                        "title": "Ecology and Evolution",
                        "units": 6.0
                    }
                    ]
                },
                {
                    "type": "CourseGroup",
                    "courseConjunction": "And",
                    "items": [
                    {
                        "type": "course",
                        "subject": "BIOL",
                        "number": "6A",
                        "title": "Form and Function in the Biological World",
                        "units": 6.0
                    },
                    {
                        "type": "course",
                        "subject": "BIOL",
                        "number": "6CH",
                        "title": "Ecology and Evolution - HONORS",
                        "units": 6.0
                    }
                    ]
                },
                {
                    "type": "CourseGroup",
                    "courseConjunction": "And",
                    "items": [
                    {
                        "type": "course",
                        "subject": "BIOL",
                        "number": "6AH",
                        "title": "Form and Function in the Biological World - HONORS",
                        "units": 6.0
                    },
                    {
                        "type": "course",
                        "subject": "BIOL",
                        "number": "6CH",
                        "title": "Ecology and Evolution - HONORS",
                        "units": 6.0
                    }
                    ]
                }
                ]
            }
            },
            {
            "receiving": {
                "type": "CourseGroup",
                "courseConjunction": "And",
                "items": [
                {
                    "type": "course",
                    "subject": "CHEM",
                    "number": "1A",
                    "title": "General Chemistry",
                    "units": 3.0
                },
                {
                    "type": "course",
                    "subject": "CHEM",
                    "number": "1AL",
                    "title": "General Chemistry Laboratory",
                    "units": 2.0
                },
                {
                    "type": "course",
                    "subject": "CHEM",
                    "number": "1B",
                    "title": "General Chemistry",
                    "units": 4.0
                }
                ]
            },
            "sending": {
                "type": "CourseGroup",
                "courseConjunction": "Or",
                "items": [
                {
                    "type": "CourseGroup",
                    "courseConjunction": "And",
                    "items": [
                    {
                        "type": "course",
                        "subject": "CHEM",
                        "number": "1A",
                        "title": "General Chemistry I",
                        "units": 5.0
                    },
                    {
                        "type": "course",
                        "subject": "CHEM",
                        "number": "1B",
                        "title": "General Chemistry II",
                        "units": 5.0
                    },
                    {
                        "type": "course",
                        "subject": "CHEM",
                        "number": "1C",
                        "title": "General Chemistry III",
                        "units": 5.0
                    }
                    ]
                },
                {
                    "type": "CourseGroup",
                    "courseConjunction": "And",
                    "items": [
                    {
                        "type": "course",
                        "subject": "CHEM",
                        "number": "1AH",
                        "title": "General Chemistry I - HONORS",
                        "units": 5.0
                    },
                    {
                        "type": "course",
                        "subject": "CHEM",
                        "number": "1BH",
                        "title": "General Chemistry II - HONORS",
                        "units": 5.0
                    },
                    {
                        "type": "course",
                        "subject": "CHEM",
                        "number": "1CH",
                        "title": "General Chemistry III - HONORS",
                        "units": 5.0
                    }
                    ]
                }
                ]
            }
            },
            {
            "receiving": {
                "type": "CourseGroup",
                "courseConjunction": "And",
                "items": [
                {
                    "type": "course",
                    "subject": "CHEM",
                    "number": "3A",
                    "title": "Chemical Structure and Reactivity",
                    "units": 3.0
                },
                {
                    "type": "course",
                    "subject": "CHEM",
                    "number": "3AL",
                    "title": "Organic Chemistry Laboratory",
                    "units": 2.0
                }
                ]
            },
            "sending": {
                "type": "CourseGroup",
                "courseConjunction": "And",
                "items": [
                {
                    "type": "course",
                    "subject": "CHEM",
                    "number": "12A",
                    "title": "Organic Chemistry I",
                    "units": 5.0
                },
                {
                    "type": "course",
                    "subject": "CHEM",
                    "number": "12B",
                    "title": "Organic Chemistry II",
                    "units": 5.0
                }
                ]
            }
            },
            {
            "receiving": {
                "type": "CourseGroup",
                "courseConjunction": "And",
                "items": [
                {
                    "type": "course",
                    "subject": "CHEM",
                    "number": "3B",
                    "title": "Chemical Structure and Reactivity",
                    "units": 3.0
                },
                {
                    "type": "course",
                    "subject": "CHEM",
                    "number": "3BL",
                    "title": "Organic Chemistry Laboratory",
                    "units": 2.0
                }
                ]
            },
            "sending": {
                "type": "CourseGroup",
                "courseConjunction": "And",
                "items": [
                {
                    "type": "course",
                    "subject": "CHEM",
                    "number": "12B",
                    "title": "Organic Chemistry II",
                    "units": 5.0
                },
                {
                    "type": "course",
                    "subject": "CHEM",
                    "number": "12C",
                    "title": "Organic Chemistry III",
                    "units": 5.0
                }
                ]
            }
            },
            {
            "receiving": {
                "type": "CourseGroup",
                "courseConjunction": "And",
                "items": [
                {
                    "type": "course",
                    "subject": "MCELLBI",
                    "number": "32",
                    "title": "Introduction to Human Physiology",
                    "units": 3.0
                },
                {
                    "type": "course",
                    "subject": "MCELLBI",
                    "number": "32L",
                    "title": "Introduction to Human Physiology Laboratory",
                    "units": 2.0
                }
                ]
            },
            "sending": {
                "type": "CourseGroup",
                "courseConjunction": "And",
                "items": [
                {
                    "type": "course",
                    "subject": "BIOL",
                    "number": "40A",
                    "title": "Human Anatomy and Physiology",
                    "units": 5.0
                },
                {
                    "type": "course",
                    "subject": "BIOL",
                    "number": "40B",
                    "title": "Human Anatomy and Physiology",
                    "units": 5.0
                },
                {
                    "type": "course",
                    "subject": "BIOL",
                    "number": "40C",
                    "title": "Human Anatomy and Physiology",
                    "units": 5.0
                }
                ]
            }
            },
            {
            "receiving": {
                "type": "course",
                "subject": "PHYSICS",
                "number": "7C",
                "title": "Physics for Scientists and Engineers",
                "units": 4.0
            },
            "sending": {
                "type": "CourseGroup",
                "courseConjunction": "And",
                "items": [
                {
                    "type": "course",
                    "subject": "PHYS",
                    "number": "4C",
                    "title": "Physics for Scientists and Engineers: Fluids, Waves, Optics and Thermodynamics",
                    "units": 6.0
                },
                {
                    "type": "course",
                    "subject": "PHYS",
                    "number": "4D",
                    "title": "Physics for Scientists and Engineers: Modern Physics",
                    "units": 6.0
                }
                ]
            }
            },
            {
            "receiving": {
                "type": "course",
                "subject": "ENGIN",
                "number": "7",
                "title": "Introduction to Computer Programming for Scientists and Engineers (MATLAB)",
                "units": 4.0
            },
            "sending": {
                "type": "NotArticulated"
            }
            },
            {
            "receiving": {
                "type": "course",
                "subject": "COMPSCI",
                "number": "61A",
                "title": "The Structure and Interpretation of Computer Programs",
                "units": 4.0
            },
            "sending": {
                "type": "NotArticulated"
            }
            },
            {
            "receiving": {
                "type": "CourseGroup",
                "courseConjunction": "And",
                "items": [
                {
                    "type": "course",
                    "subject": "MAT",
                    "number": "SCI 45",
                    "title": "Properties of Materials",
                    "units": 3.0
                },
                {
                    "type": "course",
                    "subject": "MAT",
                    "number": "SCI 45L",
                    "title": "Properties of Materials Laboratory",
                    "units": 1.0
                }
                ]
            },
            "sending": {
                "type": "NotArticulated"
            }
            },
            {
            "receiving": {
                "type": "course",
                "subject": "MEC",
                "number": "ENG C85",
                "title": "Introduction to Solid Mechanics",
                "units": 3.0
            },
            "sending": {
                "type": "NotArticulated"
            }
            },
            {
            "receiving": {
                "type": "course",
                "subject": "MEC",
                "number": "ENG 40",
                "title": "Thermodynamics",
                "units": 3.0
            },
            "sending": {
                "type": "NotArticulated"
            }
            },
            {
            "receiving": {
                "type": "course",
                "subject": "ENGIN",
                "number": "40",
                "title": "Engineering Thermodynamics",
                "units": 4.0
            },
            "sending": {
                "type": "NotArticulated"
            }
            }
        ]
        }
    

@pytest.mark.asyncio
async def test_scraper_on_de_anze_to_berk_aero(
    return_json_for_de_anze_to_berk_aero
):
    url = "https://assist.org/transfer/results?year=75&institution=79&agreement=113&agreementType=from&viewAgreementsOptions=true&view=agreement&viewBy=major&viewSendingAgreements=false&viewByKey=75%2F113%2Fto%2F79%2FMajor%2F607b828c-8ba3-411b-7de1-08dcb87d5deb"
    receiving_institution = "University of California, Berkeley"
    sending_institution = "De Anza College"

        
    
    expected = return_json_for_de_anze_to_berk_aero
    actual = await scrape_url(url, receiving_institution, sending_institution) 
    
    # assert actual == expected, f"Expected: {expected}, but got: {actual}"