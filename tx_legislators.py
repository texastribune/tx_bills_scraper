"""
This script pulls from the Sunlight Labs openstates API
to get detailed information about legislators at the state level.

Information about the specific API used can be found here:
http://python-sunlight.readthedocs.org/en/latest/services/openstates.html

To use the 'sunlight' library, you need to get an API key:
  http://services.sunlightlabs.com/

Then install the module:
  http://python-sunlight.readthedocs.org/en/latest/index.html
"""

import sunlight
import sys
import os.path
from pprint import PrettyPrinter

outfile = 'tx_state_reps_list.txt'


def find_state_reps():
  """
  Get a list of state legislators from Texas.
  """
  statereps = []
  f = os.path.exists(outfile)
  # If we've already got the list, just refer to that file
  # instead of hitting the API again.
  if f:
    # Get the file content and return it as the statereps dict
    f = open(outfile, 'r')
    statereps = eval(f.read())
    f.close()
  else:
    # Or hit the API, get the JSON, and write it to a file
    legs = sunlight.openstates.legislators(state='TX')
    l = {}
    pp = PrettyPrinter(indent=2)
    for leg in legs:
      # pp.pprint(leg)
      # print '\n\r'
      statereps.append(leg)
      leg_id = leg['leg_id']
      leg_detail = sunlight.openstates.legislator_detail(leg_id)
      # pp.pprint(leg_detail)
      # print '\n\r'
      statereps.append(leg_detail)

    # Write the JSON to a file so that data doesn't have to 
    # be pulled from the API again.
    f = open(outfile, 'w')
    f.write(str(statereps))
    f.close()

  return statereps


def main():
  # Get the initial list of state legislators
  x = find_state_reps()

if __name__ == '__main__':
  main()
