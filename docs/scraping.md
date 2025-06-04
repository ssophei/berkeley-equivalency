# Scraping

This doc will detail how the assist webpage is formatted to understand how to scrape it.

**Note:** This doc will mostly cover articulation for specific classes and not articulation for specific majors (i.e what classes are required for specific majors).

There is example html in the `example.html` file for this [site](https://assist.org/transfer/results?year=75&institution=79&agreement=124&agreementType=from&viewAgreementsOptions=true&view=agreement&viewBy=major&viewSendingAgreements=false&viewByKey=75%2F124%2Fto%2F79%2FMajor%2F23d79a84-d16c-4b58-7dee-08dcb87d5deb), which can be used as a reference, the html is formatted and edited to be easier to read. There are also comments pointing out relevant sections of code.

This guide is as of June 2025.

## Quick Aside on Formatting

- Many divs have one unique class, and we will use this class to define and name that div, and it might be referred to by the name of the class
- The syntax `{X} -> {Y}` defines a nested expression and simply means: "Y contained in X"

## How are articulations for classes defined?

On each page the articulation for each class is wrapped in a div with the class `articRow` (`rowContent` defines larger section of rows with multiple different class articulations)

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

This defines the possible ways to take classes at the source school to articulate for the target school's class.

It contains a `awc-articulation-sending` element (not div), (add more if possible)

The main content is in the div with the `view_sending__content` class which defines the following divs, again defined by their unique classes:

- `courseLine`, refer to [`rowReceiving`](#rowreceiving-div), it's the same one
- `awc-view-conjunction` refer to the discussion on [conjunctions](#conjunctions) below

## Conjunctions

Conjunctions define a set of multiple classes that can be taken to fufill a course. This can either mean multiple classes must be taken to fully articualte or there are multiple options, or both.

**Note:** Section still a work in progress, so far only defines with one conjunction (not nested)

### Brackets

Brackets are common for "and" conjunctions when defining a set of classes that must be taken to articulate the course.

Below is an example of the rendered html of a bracket:

![example bracket](images/bracket_example.png)

#### How are they defined in HTML?

The whole content of a bracket will be contained in a div with the class `bracketWrapper` (This might make it easier to scrape ands as the classes are all defined within this div) and it fill contain the following items:

    - `bracketTop`, simplify defines the top of the bracket
    - `bracketContent`, this is the section we are interested in and it defines all the classes needed, since brackets only show up in and blocks (as of our understanding right now) it will contain the `courseLine` divs in addition to the [`awc-view-conjunction`] (#awc-view-conjunction)
    - `bracketBottom`, simplfy defines the end of the bracket
    - **Note:** there may be other divs that give more information that might be important like if any bridge courses need to be taken. These divs should be explored further in the future (TODO)

### `awc-view-conjunction`

These appear to be the main way to define conjunctions and usually appear within the `rowSending -> view_sending__content` div. (but would also have to appear somewhere in the sending portion since some classes articulate more than 1 class (common for labs))

They contain the following things:

- div with class `conjunction` it then also either contains a `or` class or a `and` class depending on the type of conjction it then also wraps the text "or" or "and". This (inner div) will also have a class of either "standAlone" or "series" which will match the "cssclass" tag of the actual `awc-view-conjunction`. I dont fully understand the meaning of this tag yet.

### Exampels

#### Single or layout

`rowSending -> view_sending__content` then within that we have `courseLine` for the first option `awc-view-conjunction` with an `or` class and then another `courseLine` for the second option

#### Single and layout

`rowSending -> view_sending__content -> bracketWrapper` then within that we have `bracketTop` then `bracketContent` (which then contains looks simlar to the Single or layout except the `awc-view-conjunction` is with an and) and finally `bracketBottom`

## TODO

Investigate these cases:

- [ ] [Multiple "and"s stacked](https://assist.org/transfer/results?year=75&institution=79&agreement=105&agreementType=from&viewAgreementsOptions=true&view=agreement&viewBy=major&viewSendingAgreements=false&viewByKey=75%2F105%2Fto%2F79%2FMajor%2F3600bdbe-e56c-4bb8-7e00-08dcb87d5deb)
- [x] [Single and](https://assist.org/transfer/results?year=75&institution=79&agreement=121&agreementType=from&viewAgreementsOptions=true&view=agreement&viewBy=major&viewSendingAgreements=false&viewByKey=75%2F121%2Fto%2F79%2FMajor%2F6419da5a-b4fd-4922-7ddb-08dcb87d5deb)
- [ ] Cases where there is extra information about a class such as if it has to be taken as a bridge course in addition other cases of addtional info exist for example in the [IVC to Berk (Analytics)](https://assist.org/transfer/results?year=75&institution=79&agreement=124&agreementType=from&viewAgreementsOptions=true&view=agreement&viewBy=major&viewSendingAgreements=false&viewByKey=75%2F124%2Fto%2F79%2FMajor%2F23d79a84-d16c-4b58-7dee-08dcb87d5deb) with the "Regular and honors courses may be combined to complete this series"
- [ ] Articulate multiple classes on target side (for example when target school splits lab and lecture but source has it in one)
