# 🔍 ASSIST.org Transfer Results URL Scheme

The ASSIST.org platform provides articulation agreements between California Community Colleges (CCCs) and CSU/UC institutions. Its URL structure encodes specific institution IDs and parameters to navigate to particular agreement views. Below is an analysis of the URL scheme:

## 📄 Example URL: https://assist.org/transfer/results?year=75&institution=2&agreement=79&agreementType=to&viewAgreementsOptions=true&view=agreement&viewBy=major&viewSendingAgreements=false&viewByKey=75%2F2%2Fto%2F79%2FAllMajors

## 🔧 Parameter Breakdown

| Parameter                    | Meaning                                                                 |
|------------------------------|-------------------------------------------------------------------------|
| `year=75`                    | Internal code for the academic year (years form 1950) |
| `institution=2`              | ID for the **sending institution** (a California Community College)    |
| `agreement=79`               | ID for the **receiving institution** (a CSU or UC campus)              |
| `agreementType=to`           | Indicates direction: CCC **to** CSU/UC                                 |
| `viewAgreementsOptions=true`| Enables options related to agreement views                             |
| `view=agreement`             | Specifies that an articulation agreement is being viewed               |
| `viewBy=major`               | Indicates articulation is grouped by major                             |
| `viewSendingAgreements=false`| Used to toggle sending institution’s view (typically false here)      |
| `viewByKey=75%2F2%2Fto%2F79%2FAllMajors` | Encodes a compound key that defines the full agreement context |

## 🧠 Understanding `viewByKey`

This is a URL-encoded string: viewByKey=75%2F2%2Fto%2F79%2FAllMajors

Decoded: 75/2/to/79/AllMajors

| Segment     | Meaning                                         |
|-------------|-------------------------------------------------|
| `75`        | Year code                                       |
| `2`         | Sending CCC ID                                  |
| `to`        | Transfer direction (always from CCC to CSU/UC)  |
| `79`        | Receiving institution ID (CSU/UC)               |
| `AllMajors` | Special keyword to request articulation across **all majors** |

## ✅ Summary

This URL scheme is a structured, parameterized way to load specific articulation data between California Community Colleges and CSU/UCs on ASSIST.org. By modifying the `institution`, `agreement`, and `viewByKey` fields appropriately, you can programmatically or manually navigate to articulation pages for any CCC–CSU/UC combination, including listings for all available majors.

Let me know if you'd like to automate this for bulk querying or scraping.
