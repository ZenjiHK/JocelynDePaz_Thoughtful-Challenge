from robocorp.tasks import task
from robocorp import workitems
from Aljazeera import Aljazeera
import logging

scraper = Aljazeera()
news_data = []

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

@task
def process_news():
    """
    Main task that processes the news by configuring, searching, filtering, and saving to Excel.
    """
    try:
        for item in workitems.inputs:
            try:
                # Configure the scraper
                search_phrase = item.payload.get('search_phrase')
                max_results = item.payload.get('max_results', 1)
                sort_by = item.payload.get('sort_by')
                scraper.configure(search_phrase, max_results, sort_by)

                # Open the site
                scraper.open_site()

                # Initiate the search
                scraper.initiate_search()

                # Perform the search
                scraper.search_news()

                # Filter and sort the results
                scraper.filter_and_sort_results()

                # Load more results if necessary
                scraper.load_more_results()

                # Extract the latest news
                news_data = scraper.extract_latest_news()

                # Save the news data to work items
                for data in news_data:
                    workitems.outputs.create(payload=data)
                    logging.info(f"Work item created for news: {data['title']}")

                # Save the news data to Excel
                scraper.save_to_excel(news_data)

                # Finalize the process
                scraper.close_browser()

                # Mark the work item as done
                item.done()
            except Exception as err:
                handle_exceptions(err, item)

    except Exception as general_err:
        logging.error(f"General error in processing task: {str(general_err)}")
        raise

def handle_exceptions(err, work_item):
    """
    Handles exceptions by logging the error and marking the work item as failed.
    :param err: The exception that occurred.
    :param work_item: The work item that was being processed when the exception occurred.
    """
    error_message = str(err)
    logging.error(f"Error: {error_message}")
    
    if "NETWORK" in error_message:
        exception_type = 'APPLICATION'
        code = 'NETWORK_ERROR'
    elif "NAVIGATION" in error_message:
        exception_type = 'APPLICATION'
        code = 'NAVIGATION_ERROR'
    elif "DATA_PROCESSING" in error_message:
        exception_type = 'APPLICATION'
        code = 'DATA_PROCESSING_ERROR'
    else:
        exception_type = 'APPLICATION'
        code = 'UNCAUGHT_ERROR'
    
    work_item.inputs.current.fail(
        exception_type=exception_type,
        code=code,
        message=error_message
    )
    logging.error(f"Work item failed with error: {error_message}")