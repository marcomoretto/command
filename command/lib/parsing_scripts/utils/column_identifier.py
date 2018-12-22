def sample_column_identifier(query,header):
    """Tries to automatically identify the header column that contains the raw data given some query information (like the dye color)

    Multi-channel array might have different dye color on different samples (dye-swap) and thus it would be tedious to manually
    define it for each single sample. This function tries to do it for you and is tipically invoked for the SOFT sample files.

    PARAMETERS:
        *query* (string): The query string is usually something that contains information about the color i.e. cy3, red, green etc.

        *header* (list): The header is a list of string from which to chose one that will match the query

    """
    
    # Identifies the relevant sample data column based on a channel/color label query term in 3 steps
    
    # Initializations (all LOWER case!)
    synonymn_set = [set(['cy 5','cy5','red','f635','f633','f632','rmedian','alexa fluor 647','alexa647','647nm','cyanine5','rsignal','cy5-dutp','cy5-dctp']),set(['cy 3','cy3','green','f532','f543','gmedian','alexa fluor 555','alexa555','555nm','cyanine3','gsignal','cy3-dutp','cy3-dctp'])]
    preferred_term = ['median','spot median','mean','spot mean','raw','signal','sig','foreground','intensity']    # A 'list' so the order represents the preference
    undesired_term = ['bgmedian','background','bg','cyanine5l','cyanine3l','051409_1353(1)',
    '051409_1353(v3)','051409_1240(1)','051409_1240(v3)','051409_1052(1)','051409_1052(v3)',
    '051409_1204(1)','051409_1204(v3)','051409_1128(1)','051409_1128(v3)','051409_1317(1)',
    '051409_1317(v3)','062309_1304(1)','062309_1304(v3)','062309_1152(1)','062309_1152(v3)',
    '062309_1228(1)','062309_1228(v2)','062309_1341(1)','062309_1341(v3)','062309_1417(1)',
    '062309_1417(v2)','062309_1453(1)','062309_1453(v3)','062309_1340','071009_1246(1)',
    '071009_1246(v2)','071009_1511(1)','071009_1511(v3)','071009_1435(1)','071009_1435(v3)',
    '071009_1359(1)','071009_1359(v3)','071009_1322(1)','071009_1322(v3)','071009_1547(1)',
    '071009_1547(v3)','071009_1511(1)','071009_1511(v3)','070709_1511(1)','070709_1511(v3)',
    '070709_1435(1)','070709_1435(v3)','070709_1210(1)','070709_1210(v3)','070709_1246(1)',
    '070709_1246(v3)','070709_1322(1)','070709_1322(v3)','070709_1359(1)','070709_1359(v3)',
    'ignored']    # A 'list' so the order represents the preference
    ignore_term = ['imagene:signal','bck_median']

    
    # 1. Find the synonymn set that contains the query
    hit_set = None
    for s in synonymn_set:
        if query.lower() in s:
            hit_set = s
            break
    if hit_set is None:
        return []
    
    # 2. Identify all the columns that contain any of the query's synonymns    
    col_candidates = []    
    for col in header:
        for syn in hit_set:
            if syn in col.lower():
                col_candidates.append(col)
    if not col_candidates:
        return []
    
    # 3.a If only one column remains, check for undesired terms
    col_identified = []
    if col_candidates and len(col_candidates)==1:
        undesired = [x in col_candidates[0].lower() for x in undesired_term]
        if not sum(undesired):
            col_identified.append(col_candidates[0])
        return col_identified
    # 3.b If more than one column remains, select a -hopefully- single column based on preferred type of measurement value and undesired terms            
    elif col_candidates and len(col_candidates)>1:
        for term in preferred_term:
            for col_cand in col_candidates:
                purged_col_cand = col_cand.lower()
                for t in ignore_term:
                    purged_col_cand = purged_col_cand.replace(t, '').strip()
                # This part is a bit shifty in the sense that it only looks for preferred terms at the end or beginning and might not work for long descriptions of column labels ... so far this issue has not come up    
                if col_cand.lower().startswith(term) or col_cand.lower().endswith(term) or purged_col_cand.startswith(term) or purged_col_cand.endswith(term):
                    col_identified.append(col_cand)
            if col_identified and len(col_identified)==1:
                return col_identified  
            elif col_identified and len(col_identified)>1:    # If more than one column is returned, try and remove columns based on undesired terms   
                col_identified_cleaned = []
                for col in col_identified:
                    undesired = [x in col.lower() for x in undesired_term]
                    if not sum(undesired):
                        col_identified_cleaned.append(col)
                return col_identified_cleaned        