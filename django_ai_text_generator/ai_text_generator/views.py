from django.shortcuts import render
from django.conf import settings
from django.shortcuts import render
from django.http import JsonResponse
import requests
import urllib.parse
from django.http import HttpResponseRedirect








def generate_text(request):
    if request.method == 'POST':
        query = request.POST.get('query', '').strip()

        if not query:
            return JsonResponse({"error": "Please enter a valid query."}, status=400)

        # Define a list of common commands and their corresponding URLs
        commands = {
            "open youtube": "https://www.youtube.com",
            "open facebook": "https://www.facebook.com",
            "open google": "https://www.google.com",
            "open twitter": "https://www.twitter.com",
            "open instagram": "https://www.instagram.com",
            # Add more commands as needed
        }

        # Check if the query matches any predefined command
        for command, url in commands.items():
            if command in query.lower():
                return HttpResponseRedirect(url)  # Redirect to the URL for the command

        # If no predefined command is found, proceed with Wolfram and Wikipedia APIs
        wolfram_url = "http://api.wolframalpha.com/v2/query"
        wikipedia_url = "https://en.wikipedia.org/api/rest_v1/page/summary/"

        params = {
            "input": query,
            "format": "plaintext",
            "output": "JSON",
            "appid": settings.WOLFRAM_APP_ID
        }

        try:
            # Attempt to get data from Wolfram Alpha
            response = requests.get(wolfram_url, params=params)
            response.raise_for_status()
            wolfram_data = response.json()

            if 'queryresult' in wolfram_data and wolfram_data['queryresult'].get('pods', []):
                result = [{"pod_title": pod['title'], "text": subpod.get('plaintext', 'No text available')}
                          for pod in wolfram_data['queryresult']['pods'] for subpod in pod.get('subpods', [])]
                return JsonResponse({"result": result, "query": query})

            # If Wolfram Alpha returns no results, fetch from Wikipedia
            encoded_query = urllib.parse.quote(query)  # Encode the query for safe URL usage
            wiki_response = requests.get(wikipedia_url + encoded_query)
            wiki_response.raise_for_status()
            wiki_data = wiki_response.json()

            if "extract" in wiki_data:
                return JsonResponse({"result": [{"pod_title": "Wikipedia Summary", "text": wiki_data["extract"]}], "query": query})
            else:
                return JsonResponse({"error": "No extract found on Wikipedia."}, status=404)

            # If no results from Wolfram or Wikipedia
            return JsonResponse({"error": "No relevant results found."}, status=404)

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                return JsonResponse({"error": "No results found for this query."}, status=404)
            return JsonResponse({"error": f"Failed to connect to APIs. {str(e)}"}, status=500)

        except requests.exceptions.RequestException as e:
            return JsonResponse({"error": f"Failed to connect to APIs. {str(e)}"}, status=500)

    return render(request, 'pages/generate_text.html')
