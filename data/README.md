# GDELT Project Data

## What is GDELT?

GDELT (Global Data on Events Location and Tone) is an open dataset that monitors global news events in real-time. It captures more than 200 million geolocated events from 1979 to the present, offering a comprehensive view of human society and conflict. GDELT processes data in over 65 languages and is freely available for analysis, exploration, and export through various cloud-based services.

### Key GDELT Services

- **Analysis Service**: GDELT allows users to query, analyze, and download up to 20,000 records at a time, across 57-58 fields.
  - Each event is coded using the CAMEO (Conflict and Mediation Event Observations) coding framework.
  - Extensive data dictionaries and codebooks are available to interpret these codes.
  
- **Google BigQuery Integration**: The size of GDELT datasets often makes them challenging to handle locally. Through BigQuery, users can query and analyze these datasets in real-time with SQL.
  - Datasets are updated every 15 minutes and are available for integration into analysis workflows.

- **Real-time Global Coverage**: GDELT tracks news in 65 languages, translating and analyzing news reports from both Western and non-Western media.
  - It provides real-time information on events like protests, conflicts, and natural disasters, while identifying key quotes, images, and relevant geographical information.

### Applications of GDELT Data

- **Conflict Tracking**: GDELT is frequently used for tracking geopolitical events. For example, using a query on "Boko Haram" in Nigeria, you can track reported attacks, military actions, and peace talks in real-time.
- **Sentiment Analysis**: GDELT applies natural language processing techniques to assign sentiment scores to news articles, making it possible to track public opinion on various global events.
- **Data Visualization**: You can visualize GDELT data using tools like Google Data Studio or custom-built dashboards to gain insights into the distribution and intensity of events globally.

---

## GDELT Data Dictionary

### Introduction

The GDELT Event Database is structured in a tab-delimited format (with a `.csv` extension). The following are descriptions of the main fields present in the dataset, based on the GDELT 2.0 Event Codebook.

### Event Table

- **GlobalEventID**: (integer) A globally unique identifier for each event. It is not recommended to sort by this field; use the date fields instead.
  
- **Day**: (integer) The date of the event in YYYYMMDD format.

- **MonthYear**: (integer) The event date in YYYYMM format.

- **Year**: (integer) The event date in YYYY format.

- **FractionDate**: (floating point) An alternative formatting of the event date, computed as a fraction of the year. Useful for temporal analysis.

### Actor Fields

- **Actor1Code**: (string) The full CAMEO code for Actor 1, indicating geographic, ethnic, and role attributes.
  
- **Actor1Name**: (string) The full name of Actor 1. Examples include political leaders, countries, or ethnic groups.

- **Actor1CountryCode**: (string) The three-character CAMEO code representing the country of Actor 1.

- **Actor1KnownGroupCode**: (string) If Actor 1 is a known organization (e.g., UN, al-Qaeda), this field holds the group’s code.

- **Actor1EthnicCode**: (string) The CAMEO code for the ethnic group of Actor 1, if available.

- **Actor1Religion1Code**: (string) The primary religious affiliation of Actor 1.

- **Actor1Religion2Code**: (string) The secondary religious affiliation of Actor 1, if applicable.

- **Actor1Type1Code**: (string) CAMEO code representing the role of Actor 1 (e.g., Political Elite, Military Officer).

The same fields apply to **Actor2** (e.g., `Actor2Code`, `Actor2Name`, etc.).

### Event Action Attributes

- **IsRootEvent**: (integer) A flag indicating whether this is the primary event in the document.

- **EventCode**: (string) The CAMEO code representing the action performed by Actor 1 on Actor 2.

- **EventBaseCode**: (string) The level 2 event code, used for higher-level aggregation.

- **EventRootCode**: (string) The root event code, representing the most general form of the event.

- **QuadClass**: (integer) A classification of the event into four types: Verbal Cooperation, Material Cooperation, Verbal Conflict, Material Conflict.

- **GoldsteinScale**: (floating point) A score between -10 and +10 representing the event’s impact on stability. Negative values indicate destabilizing events, while positive values are stabilizing.

- **NumMentions**: (integer) The number of mentions of the event in the source documents.

- **NumSources**: (integer) The number of unique sources that mention this event.

- **NumArticles**: (integer) The number of articles in which the event is mentioned.

- **AvgTone**: (numeric) The average tone of articles discussing this event, ranging from -100 (extremely negative) to +100 (extremely positive).

### Event Geography

- **Actor1Geo_Type**: (integer) The resolution of the geographic match (1 = Country, 2 = US State, 3 = US City, 4 = World City, 5 = Administrative Division).

- **Actor1Geo_Fullname**: (string) The full human-readable name of the location matched for Actor 1.

- **Actor1Geo_CountryCode**: (string) The country code for the location of Actor 1.

- **Actor1Geo_ADM1Code**: (string) The administrative division of Actor 1's location.

- **Actor1Geo_Lat**: (floating point) The latitude of the Actor 1's location.

- **Actor1Geo_Long**: (floating point) The longitude of Actor 1's location.

These fields are repeated for Actor 2 and for the action location (prefixed with `Actor2` or `Action`).

### Mentions Table

- **GlobalEventID**: (integer) The unique ID of the event that was mentioned in the article.
- **MentionTimeDate**: (integer) The timestamp of when the event was mentioned in YYYYMMDDHHMMSS format.
- **MentionType**: (integer) The source collection of the document (e.g., web, citation only, archive).
- **MentionSourceName**: (integer) A human-readable identifier of the document’s source.
- **MentionIdentifier**: (integer) A unique identifier for the source document.
- **Confidence**: (integer) GDELT’s confidence in its extraction of the event, ranging from 10% to 100%.

---

This README provides a high-level overview of GDELT services and its main fields. For more detailed field descriptions, you can refer to the full [GDELT Event Codebook](http://data.gdeltproject.org/documentation/GDELT-Event_Codebook-V2.0.pdf).

