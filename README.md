# Jenny job search

A simple tool to generate and host an RSS-feed containing the most recently-posted job adverts at the Arbeitsargentur, at Microsoft's expense.

## Setting up the search

Copy the `.env.template` file to `.env` and add an e-mail address and name for the feed author. The list of search terms is configured in `jobs.py`.

You can run the `jobs.py` script to dump the list of jobs, and the `rss.py` script to dump it as RSS.

## Setting up the search on Github

The repository includes workflows to generate the RSS on a timer and upload it to Github Pages. This way, the RSS is automatically updated, and the feed is hosted on your behalf, for free, by Github.

To deploy to a different fork, the environment variables need to be configured in the Github UI for the target environment in the target project. The workflows use the environment named `build`.