# 10/1, Aidan's Notes on Machine Learning for this project
## Question
What will be the highest grossing movie domestically in a calendar year?

## What to do
There are two clear ways to go about this question. The first would be to predict grosses for every movie that is coming out in a given year. The second would be to use some sort of classification model to predict the likelihood of a movie being the highest grossing domestically in a given year. The first option offers substantially more flexibility. Additionally, to have strong chances of victory in the (https://polymarket.com/event/highest-grossing-movie-in-2024)[polymarket], we would need a time series model anyways given the chances of two movies being close in gross after releasing.
It is clear that there would need to be 2 models, one for after the movie has come out and one for before. This is because after a movie comes out, we have much more information. My opinion then is that beforehand, we work on predicting the parameters of the time series and then to get the total gross, we use the time series model.

## How the time series model would work
There are two main components to consider:
1. relevant multiples
2. broader seasonality and holidays

Here are some of the relevant multiples and numbers:
- Size of the opening weekend
- Thursday previews to Opening Weekend
- Opening Weekend to Total Gross
- Weekend to weekday multiple
- Weekend to weekend multiple
- Basically every back to back weekday pair has a relevant multiple that is generally consistent over the course of the movie's release (especially true for high grossing movies with large marketing budgets)
  - Friday to Saturday
  - Saturday to Sunday
  - Sunday to Monday
  - Monday to Tuesday
  - Tuesday to Wednesday
  - Wednesday to Thursday
  - Thursday to Friday

Here are some of the broader seasonality and holidays:
- Holidays with no school
- Summer or winter releases
- Depending on the audience of the movie, could have higher Tuesdays or weekdays in general

## How to get the information
I would say there are two clear options for how to get the predicted multiples:
1. Use a classification model to find the most similar movies to the one we are predicting, and use a weighted average of their multiples
2. Use a regression model to predict the multiples directly

## How use the data
Before a movie comes out, we generate a prior time series. Then, after the movie comes out, we update this prior time series with the actual data and then re-predict the multiples.

## Type of the time series
This does not seem like an ARIMA. The reason this does not seem like an ARIMA is due to exponential drift. It seems like it would be better to predict the daily multiples and just generate the time series from that and then the final gross from the sum of the predicted daily grosses.
