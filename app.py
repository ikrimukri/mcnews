import mediacloud.api
from datetime import date
import time
import pandas as pd
import os

def get_news_data(keyword, days_back=1):
    """
    Fetch news data based on keyword and return as a DataFrame.
    
    Args:
        keyword (str): Search keyword
        days_back (int): Number of days to look back from today
    
    Returns:
        pandas.DataFrame: News data with publish date, media name, title, and URL
    """
    # Initialize API
    API_KEY = '4b6d7e86d1251e65c7f7f6201bd6bfb959c312f8'
    mc = mediacloud.api.SearchApi(API_KEY)
    
    end = date.today()
    start = end  # For single day search (today)
    
    # Create empty lists for data
    publish_dates = []
    media_names = []
    titles = []
    urls = []
    
    # Fetch stories with pagination
    pagination_token = None
    more_stories = True
    total_stories = 0
    
    print(f"Searching for news about '{keyword}'...")
    
    while more_stories:
        try:
            # Get batch of stories
            stories, pagination_token = mc.story_list(
                keyword,
                start_date=start,
                end_date=end
            )
            
            if not stories:
                print("No more stories found.")
                more_stories = False
                break
            
            # Extract data
            for story in stories:
                publish_dates.append(story.get('publish_date', ''))
                media_names.append(story.get('media_name', ''))
                titles.append(story.get('title', ''))
                urls.append(story.get('url', ''))
            
            total_stories += len(stories)
            print(f"Fetched {len(stories)} stories. Total so far: {total_stories}")
            
            # Check if more stories available
            more_stories = pagination_token is not None
            
            # Rate limiting to be respectful of API
            time.sleep(1)
            
        except Exception as e:
            print(f"Error occurred: {e}")
            break
    
    # Create DataFrame
    news_df = pd.DataFrame({
        'publish_date': publish_dates,
        'media_name': media_names,
        'title': titles,
        'url': urls
    })
    
    return news_df

def save_to_csv(dataframe, filename='news_data.csv', directory=None):
    """
    Save the news DataFrame to a CSV file.
    
    Args:
        dataframe (pandas.DataFrame): DataFrame to save
        filename (str): Name of CSV file
        directory (str, optional): Directory to save the file in
    
    Returns:
        str: Path to the saved CSV file
    """
    if directory and not os.path.exists(directory):
        os.makedirs(directory)
    
    filepath = os.path.join(directory, filename) if directory else filename
    
    try:
        dataframe.to_csv(filepath, index=False, encoding='utf-8')
        print(f"Successfully saved {len(dataframe)} records to {filepath}")
        return filepath
    except Exception as e:
        print(f"Error saving CSV: {e}")
        return None

if __name__ == "__main__":
    # Get keyword from user or use default
    keyword = input("Enter search keyword (or press Enter for 'Bangladesh'): ").strip()
    if not keyword:
        keyword = 'Bangladesh'
    
    # Get news data
    news_df = get_news_data(keyword)
    
    # Display summary
    print(f"\nFound {len(news_df)} articles about '{keyword}'")
    if not news_df.empty:
        print("\nFirst 5 articles:")
        for i, row in news_df.head().iterrows():
            print(f"{i+1}. {row['title']} ({row['media_name']})")
        
        # Ask if user wants to save to CSV
        save_option = input("\nSave results to CSV? (y/n): ").lower().strip()
        if save_option.startswith('y'):
            save_to_csv(news_df, f"{keyword}_news_data.csv")
    else:
        print("No articles found.")