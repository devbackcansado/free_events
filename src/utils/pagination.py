from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator


def generate_pagination_by_models(serializer, page_number, page_size=3):
    """
    Generates pagination data for a given serializer and page number.

    Args:
        serializer: The serializer containing the data to paginate.
        page_number (int): The current page number to retrieve.
        page_size (int): The number of objects to display per page.

    Returns:
        dict: A dictionary containing pagination information:
            - success (bool): Indicates if the pagination was successful.
            - previous_page (int or None): The previous page number, or None if there is no previous page.
            - next_page (int or None): The next page number, or None if there is no next page.
            - num_pages (int or None): The total number of pages, or None if there are no pages.
            - data (list): A list of objects for the current page.

    Example:
        >>> serializer = ContactSerializer(Contact.objects.all(), many=True)
        >>> generate_pagination_by_models(serializer, 1, 3)
        {
            "success": True,
            "previous_page": None,
            "next_page": 2,
            "num_pages": 3,
            "total": 10,
            "data": [
                {
                    "id": 1,
                    "name": "John Doe",
                    "email": "jhon@doe.com"
                },
                ...
            ]
        }
    """
    paginator = Paginator(serializer, page_size)

    num_pages = paginator.num_pages
    try:
        objects = paginator.page(page_number)
    except PageNotAnInteger:
        objects = paginator.page(1)
    except EmptyPage:
        objects = paginator.page(num_pages)

    return {
        "success": True,
        "previous_page": objects.has_previous() and objects.previous_page_number() or None,
        "next_page": objects.has_next() and objects.next_page_number() or None,
        "num_pages": num_pages or None,
        "total": paginator.count,
        "data": list(objects),
    }


def generate_pagination_by_sql(queryset, page_number, page_size=3):
    """
    Generates pagination data for a given queryset and page number.

    Args:
        queryset: The queryset containing the data to paginate.
        page_number (int): The current page number to retrieve.
        page_size (int): The number of objects to display per page.

    Returns:
        dict: A dictionary containing pagination information:
            - success (bool): Indicates if the pagination was successful.
            - previous_page (int or None): The previous page number, or None if there is no previous page.
            - next_page (int or None): The next page number, or None if there is no next page.
            - num_pages (int or None): The total number of pages, or None if there are no pages.
            - data (list): A list of objects for the current page.

    Example:
    """

    if queryset:
        total_pages = (queryset[0]["total"] + page_size - 1) // page_size
        has_next_page = page_number < total_pages
        has_previous_page = page_number > 1
        num_pages_range = total_pages
    else:
        total_pages = None
        has_next_page = None
        has_previous_page = None
        num_pages_range = None

    return {
        "success": True,
        "previous_page": page_number - 1 if has_previous_page else None,
        "next_page": page_number + 1 if has_next_page else None,
        "num_pages": num_pages_range,
        "total": queryset[0]["total"] if queryset else 0,
        "data": queryset,
    }
