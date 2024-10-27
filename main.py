import sys
from israel_trends import fetch_trends as fetch_israel_trends
from lebanon_trends import fetch_trends as fetch_lebanon_trends
from iran_trends import fetch_trends as fetch_iran_trends

def main():
    if len(sys.argv) > 1:
        country = sys.argv[1].upper()
        if country == "IL":
            result = fetch_israel_trends()
        elif country == "LB":
            result = fetch_lebanon_trends()
        elif country == "IR":
            result = fetch_iran_trends()
        else:
            print(f"Unsupported country code: {country}")
            print("\nSupported country codes:")
            print("IL - Israel")
            print("LB - Lebanon")
            print("IR - Iran")
            return
            
        if result:
            print("\nTrending Searches:")
            for trend in result['trends_data']:
                print(f"\n{trend['title']}")
                if trend['related']:
                    print("Related searches:")
                    for related in trend['related']:
                        print(f"- {related}")
                        
            if 'analysis' in result:
                print("\nAnalysis:")
                print(result['analysis'])
        else:
            print("\nNo results found. This could be due to:")
            print("- No trending searches available")
            print("- API rate limits or connectivity issues")
    else:
        print("\nUsage: python main.py [country_code]")
        print("\nSupported country codes:")
        print("IL - Israel")
        print("LB - Lebanon")
        print("IR - Iran")
        print("\nExample: python main.py IL")

if __name__ == "__main__":
    main()
