# Scraping

This doc will detail how the assist webpage is formatted to understand how to scrape it.

**Note:** This doc will mostly cover articulation for specific classes and not articulation for specfic majors (i.e what classes are required for specific majors).

There is example html in the `example.html` file for this [site](https://assist.org/transfer/results?year=75&institution=79&agreement=124&agreementType=from&viewAgreementsOptions=true&view=agreement&viewBy=major&viewSendingAgreements=false&viewByKey=75%2F124%2Fto%2F79%2FMajor%2F23d79a84-d16c-4b58-7dee-08dcb87d5deb), which can be used as a reference, the html is formatted and edited to be easier to read. There are also comments pointing out relevenet sections of code.

This guide is as of June 2025.

## Quick Aside on Formatting

- Many divs have one unique class, and we will use this class to define and name that div, and it might be referred to by the name of the class
- The syntax `{X} -> {Y}` defines a nested expression and simply means: "Y contained in X"

## How are articulations for classes defined

On each page the articualtion for each class is wrapped in a div with the class `articRow`

From there we can break down the div into three different divs which have the following classes: `rowReceiving`, `rowDirection`, and `rowSending`. From now on we will refer to these divs with their respective class name.

### `rowReceiving` div

This defines the details of a class at the target school. (non cc)

As of right now it only contains the the div with class `courseLine` which contains the following divs defined by their unique classes:

- `prefixCourseNumber`, the text this div wraps, as the name implies, defines the course number (ex MATH 1B)
- `courseTitle`, the text this div wraps gives the general course title although it might not be super detailed (Ex: Calculus (however this is used for both Calc 1 and Calc 2 for Berk))
- `courseUnits`, the text this div wraps are the number of units for the course. (Ex: 4.00), it also contains a hidden span with the class `visually-hidden` that contains the word "units"

### `rowDirection` div

Don't fully understand the purpose of this div, but it displays an arrow from either the source to target or vice versa for that specific class.

### `rowSending` div

This defines the possible ways to take classes at the source school to articulate for the target schools class.

It contains a `awc-articulation-sending` element (not div), (add more if possible)

The main content is in the div with the `view_sending__content` class which defines the following divs, again defined by their unique classes:

- `courseLine`, refer to [`rowReceiving`](#rowreceiving-div), its the same one
- `awc-view-conjunction` refer to the discussion on [conjungtions](#conjungtions-or-or-and) below

## Conjungtions NOT FINSHED ([or] or [and])

**Note:** So far only defines with one conjuntion (not nested)

### `awc-view-conjunction`

These appear to be the main way to define conjungtions and usually appear within the `rowSending -> view_sending__content` div. (but would also have to appear somewhere in the sending portion since some classes articualte more than 1 class (common for labs))

They contain the following things:

- div with class `conjunction or standAlone` which then contains "or" (or "and"??) as text

Example:

## TODO

Investigate these cases:

- [Multiple "and"s stacked](https://assist.org/transfer/results?year=75&institution=79&agreement=105&agreementType=from&viewAgreementsOptions=true&view=agreement&viewBy=major&viewSendingAgreements=false&viewByKey=75%2F105%2Fto%2F79%2FMajor%2F3600bdbe-e56c-4bb8-7e00-08dcb87d5deb)
- [Single and](https://assist.org/transfer/results?year=75&institution=79&agreement=121&agreementType=from&viewAgreementsOptions=true&view=agreement&viewBy=major&viewSendingAgreements=false&viewByKey=75%2F121%2Fto%2F79%2FMajor%2F6419da5a-b4fd-4922-7ddb-08dcb87d5deb)
