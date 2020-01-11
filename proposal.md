# Authors: Lori Feng, Roc Zhang, Cari Gostic

### See [original project](https://github.com/UBC-MDS/DSCI-532_group-203_Lab1-2)

## Section 1: Motivation and Purpose

Central Park is a famous public park in New York City, and home to a considerable number of squirrels. However, because the park is so huge, those tourists, animal lovers, photographers or scientists who want to better observe squirrels may have difficulty locating a squirrel among the park's many features. Our app will display the distribution of the park’s squirrel population across the park so that squirrel lovers can find the area where they are most likely to see squirrels. On the other hand, sciurophobiacs or picnic-goers can find the park area where the fewest squirrels have been observed. Our app will also allow users to see how the distribution of squirrels changes from the morning to the afternoon, and where certain behaviors are exhibited the most in order to maximize effective squirrel-watching activities.

## Section 2: Description of the data

The 2018 Central Park Squirrel Census dataset includes 3018 unique observations. Each observation describes a single squirrel sighting, and includes information on time of observation, location of squirrel, squirrel behavior, and squirrel appearance. We limit our exploration to observation time, location and a subset of behaviors to formulate our research questions. Each observation notes a `Unique Squirrel ID`. Each behavior of interest is represented in its own column, with a boolean value that notes if a given observed squirrel exhibited that behavior. Recorded behaviors include movements (e.g. `climbing`), vocalizations (e.g. `kuks`) and interactions with humans (e.g. `approaches`). Observation location is recorded as separate latitude (`X`) and longitude (`Y`) values from which a coordinate point (`Lat/Long`) is derived. The time of observation is recorded categorically as AM or PM in the `Shift` column. This column is used to derive `Count_difference`, the difference in squirrel count in the afternoon compared to the morning. In addition to the 2018 Central Park Squirrel Census dataset, we incorporate a geoJson file to supplement location information. The geoJson file includes a `sitename` field that lists named park areas, and a `geometry` field that represents these park area boundaries as polygons. 

## Section 3: Research questions and usage scenarios
### -Research questions

1. How is the squirrel population distributed in Central Park?

2. When(morning or afternoon) is a better time to observe squirrels?

3. Where is the best place to observe squirrels exhibiting a specific behaviour?  

### -Usage scenario with tasks (tasks are indicated in brackets, i.e. [task])

John Doe works as a travelling photographer for a science magazine. He is interested in taking pictures of animals and their behaviour. When he travels to New York, he plans to spend half a day in Central Park to photograph the park’s famous squirrels. He hasn’t yet decided which part of the park he will be visit, but he wants to [find] the closest area with the most squirrels for him to observe and take pictures of. He also wants to [identify] a time of day, either the morning or afternoon, that he will have a higher chance to see squirrels eating. When John opens the “ See Squirrels in Central Park, NYC app”, he will first see a map of Central Park. Then he can click on the area on the map closest to him to see the number of observed squirrels in that area, or click multiple areas to [compare] the numbers of squirrels across several areas. Then, he can easily [decide] which area to visit based on where he is. For example, he is in Northwest corner right now, it is unnecessary for him to go all the way south to The Ramble to see more squirrels. Instead, he can just go to Central Park West zone 1. John can also filter the behaviour to eating and the app will show in which areas the most squirrels are observed eating. Based on this information, John can create clear plan to efficiently capture the pictures he desires within his limited time frame.
