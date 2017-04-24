import scipy.stats as stats
import pandas as pd
from modules.turtleGrapher.turtle_utils import generate_uri as gu
from modules.groupComparisons.sparql_queries import query

def fishers(queryUriA, queryUriB, targetUri):
    # query the blazegraph db for results
    results = query(queryUriA, queryUriB, targetUri)

    # create pandas dataframes from results
    dfA = pd.DataFrame(results[queryUriA])
    dfB = pd.DataFrame(results[queryUriB])

    # check which results from group A is in results from group B
    matchesAtoB = dfA[0].isin(dfB[0])
    # count the number of matches
    count_matchesAtoB = matchesAtoB.value_counts()
    # check which results from group B is in results from group A
    matchesBtoA = dfB[0].isin(dfA[0])
    # count the number of matches
    count_matchesBtoA = matchesBtoA.value_counts()

    # compute fisher's exact test
    # table structure is:
    #           queryUriA   queryUriB
    #   True
    #   False
    oddsratio, pvalue = stats.fisher_exact([[count_matchesAtoB[True], count_matchesBtoA[True]], [count_matchesAtoB[False], count_matchesBtoA[False]]])

    return pvalue

if __name__ == "__main__":
    '''
    For testing...
    '''
    print fishers(gu(':spfy1'),gu(':spfy2'),gu(':Marker'))
