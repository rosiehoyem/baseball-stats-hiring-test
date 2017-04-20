"""Main script for generating output.csv."""
from __future__ import division
import numpy as np
import pandas as pd

def calc_avg(df):
    """Calculate batting average: hits divided by at bats (H/AB)"""
    avg = sum(df.H)/sum(df.AB)
    return avg
    
def calc_obp(df):
    """Calculate on-base percentage: times reached base (H + BB + HBP) 
        divided by at bats plus walks plus hit by pitch plus sacrifice 
        flies (AB + BB + HBP + SF)"""
    obp = (sum(df.H) + sum(df.BB) + sum(df.HBP))/\
          (sum(df.AB) + sum(df.BB) + sum(df.HBP) + sum(df.SF))
    return obp
    
def calc_slg(df):
    """Calculate slugging average: total bases achieved on hits divided 
        by at-bats (TB/AB)"""
    slg = (sum(df.TB)/sum(df.AB))
    return slg

def calc_ops(obp, slg):
    """Calculate on-base plus slugging: on-base percentage plus 
        slugging average"""
    ops = obp + slg
    return ops

def calc_subject_stats(df, results, subject_id, subject_name, split):
    """Calculate AVG, OBP, SLG, and OPS stats for given subject and add 
        it to results array."""
    avg = calc_avg(df)
    # Round all stats to 3 decimal places
    results.append([subject_id, "AVG", split, subject_name, avg.round(3)])
    
    obp = calc_obp(df)
    results.append([subject_id, "OBP", split, subject_name, obp.round(3)])
    
    slg = calc_slg(df)
    results.append([subject_id, "SLG", split, subject_name, slg.round(3)])
    
    ops = calc_ops(obp, slg)
    results.append([subject_id, "OPS", split, subject_name, ops.round(3)])
    return results
   

def calc_pitcher_team_stats(raw_df, results, team_ids):
    """Extract relevant observations from dataframe for pitcher team subjects, 
        run stat calculations, and add to given results array."""
    for team_id in team_ids:
        team_df = raw_df[raw_df['PitcherTeamId'] == team_id]
        # Check for minimum number of plate appearances
        if sum(team_df.PA) >= 25:
            for side in ['R', 'L']:
                split = "vs " + side + "HH"
                df = team_df[team_df.HitterSide == side]
                results = calc_subject_stats(
                    df, results, team_id, 'PitcherTeamId', split
                )
    return results

def calc_hitter_team_stats(raw_df, results, team_ids):
    """Extract relevant observations from dataframe for hitter team subjects, 
        run stat calculations, and add to given results array."""
    for team_id in team_ids:
        team_df = raw_df[raw_df['HitterTeamId'] == team_id]
        # Check for minimum number of plate appearances
        if sum(team_df.PA) >= 25:
            for side in ['R', 'L']:
                split = "vs " + side + "HP"
                df = team_df[team_df.PitcherSide == side]
                results = calc_subject_stats(
                    df, results, team_id, 'HitterTeamId', split
                )
    return results

def calc_pitcher_player_stats(raw_df, results, pitcher_ids):
    """Extract relevant observations from dataframe for pitcher player subjects, 
        run stat calculations, and add to given results array."""
    for pitcher_id in pitcher_ids:
        pitcher_df = raw_df[raw_df['PitcherId'] == pitcher_id]
        for side in ['R', 'L']:
            split = "vs " + side + "HH"
            df = pitcher_df[pitcher_df.HitterSide == side]
            # Check for minimum number of plate appearances
            if sum(df.PA) >= 25:
                results = calc_subject_stats(
                    df, results, pitcher_id, 'PitcherId', split
                )
    return results
                
def calc_hitter_player_stats(raw_df, results, hitter_ids):
    """Extract relevant observations from dataframe for hitter player 
        subjects, run stat calculations, and add to given results 
        array."""
    for hitter_id in hitter_ids:
        hitter_df = raw_df[raw_df['HitterId'] == hitter_id]
        for side in ['R', 'L']:
            split = "vs " + side + "HP"
            df = hitter_df[hitter_df.PitcherSide == side]
            # Check for minimum number of plate appearances
            if sum(df.PA) >= 25:
                results = calc_subject_stats(
                    df, results, hitter_id, 'HitterId', split
                )
    return results

def main():
    # Read in ./data/raw/pitchdata.csv
    raw_df = pd.read_csv('data/raw/pitchdata.csv')

    # Create lists of subject ids
    team_ids = raw_df.PitcherTeamId.unique()
    pitcher_ids = raw_df.PitcherId.unique()
    hitter_ids = raw_df.HitterId.unique()

    # Create empty list for results
    results = []

    # Add pitcher team stats to results
    results = calc_pitcher_team_stats(raw_df, results, team_ids)

    # Add hitter team stats to reults
    results = calc_hitter_team_stats(raw_df, results, team_ids)

    # Add pitcher player stats to results
    results = calc_pitcher_player_stats(raw_df, results, pitcher_ids)

    # Add hitter player stats to results
    results = calc_hitter_player_stats(raw_df, results, hitter_ids)

    # Turn results into a dataframe, add column headers, and sort
    results_df = pd.DataFrame(
        results, columns=["SubjectId","Stat","Split","Subject","Value"]
    )
    sorted_results_df = results_df.sort_values(["SubjectId", "Stat", "Split", "Subject"])

    # write results to file
    sorted_results_df.to_csv('data/processed/output.csv', index=False)

if __name__ == '__main__':
    main()
