from bs4 import BeautifulSoup, Comment


def find_table(soup, tid):
    # Find all comments on the page
    comments = soup.find_all(string=lambda text: isinstance(text, Comment))

    # Search the comments for the table
    for comment in comments:
        if f'id="{tid}"' in comment:
            return BeautifulSoup(comment, 'html.parser')
    return None


def get_career_table(soup):
    """ Finds and returns the table on a player's page which contains his AV for each year."""
    # TODO: speed function up with position based assumptions (i.e. a QB won't have his AV in a defense table)
    titles = ['passing', 'rushing_and_receiving', 'receiving_and_rushing', 'defense', 'kicking', 'punting', 'returns',
              'games_played']  # All possible table names

    # Load each table and if it exists, check if there is an AV column in it
    for title in titles:
        table = soup.find('table', attrs={'id': title})
        if (table is not None) and ('AV' in table.text):
            return table
    return None


def get_position_group(position):
    """ Groups all positions into groups for simpler data handling. """
    if position in ['T', 'G', 'RT', 'RG', 'LT', 'LG', 'C', 'G-C', 'C-G', 'G-T', 'T-G', 'C-T', 'T-C', 'C-T-G', 'T-G-C',
                    'T-C-G', 'C-G-T', 'G-C-T', 'G-T-C']:
        return 'OL'
    elif position in ['RDT', 'LDT', 'NT', 'DT', 'NT-DT', 'DT-NT', 'DT-NT-DE', 'DE-DT-NT', 'DT-DE-NT', 'NT-DE-DT',
                      'DE-NT-DT', 'DE-NT-DT-DE', 'NT-DT-DE', 'DL']:
        return 'IDL'
    elif position in ['RDE', 'LDE', 'OLB-DE', 'LB-DE', 'DE-LB', 'DE-OLB', 'EDGE', 'E']:
        return 'DE'
    elif position in ['OLB', 'OOLB', 'MLB', 'ROLB', 'LOLB', 'LLB', 'RLB', 'LILB', 'RILB', 'ILB']:
        return 'LB'
    elif position in ['RCB', 'LCB']:
        return 'CB'
    elif position in ['SS', 'FS']:
        return 'S'
    else:
        return position


def lbs_to_kgs(weight):
    return round(weight / 2.2046)


def inches_to_cm(height):
    return round(height * 2.54)
