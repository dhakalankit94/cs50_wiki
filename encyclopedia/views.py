import markdown2
import random
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django import forms
from django.core.files.storage import default_storage
from . import util

# Search Form
class SearchForm(forms.Form):
    query = forms.CharField(label="",
        widget=forms.TextInput(attrs={'placeholder': 'Search Encyclopedia',
            'style': 'width:100%'}))

# Create new page Form
class NewPageForm(forms.Form):
    title = forms.CharField(label="", required= True, help_text="<p> Please refer <a href = https://docs.github.com/en/github/writing-on-github/basic-writing-and-formatting-syntax> Guthub's Markdown Guide</a></p>",
        widget= forms.TextInput (attrs={'placeholder': 'Enter Title'}))
    data = forms.CharField(label="", required=False,
        widget= forms.Textarea(attrs={'placeholder': 'Enter Markdown content', 'cols': 50}))

# Create Edit form
class EditPageForm(forms.Form):
    title = forms.CharField(label="", required= True, help_text="<br><h3>Enter your new entry here:</h3>",
        widget= forms.TextInput (attrs={'placeholder': 'Enter Title'}))
    data = forms.CharField(label="", required=False,
        widget= forms.Textarea(attrs={'placeholder': 'Enter Markdown content', 'cols': 50}))


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(),
        "form": SearchForm(),
    })

def entry(request, title):
    """ This view gives the entry associated with
        title.
    """
    entry = util.get_entry(title)

    if entry is None:
        return render(request, "encyclopedia/error.html",{
            "title": title,
            "form": SearchForm()
        })
    
    # If entry is not none.
    else:
        return render(request, "encyclopedia/entry.html",{
            "title": title,
            "entry": markdown2.markdown(entry),
            "form": SearchForm()
        })

def search(request):
    if request.method == "GET":
        entries_found = [] # List of partial matches
        all_entries = util.list_entries() # Capturing all the entries
        form = SearchForm(request.GET) # Getting the info from form
        # Check if the info is valid or not
        if form.is_valid():
            # Get the query to search entry
            query = form.cleaned_data["query"]
            # Check if the requested data matches with the entries
            # If matched than redirect to entry page with result lists.
            for entry in all_entries:
                if query.lower() == entry.lower():
                    title = entry
                    entry = util.get_entry(title)
                    return HttpResponseRedirect(reverse("encyclopedia:entry", args=[title]))
                # Partial matches stored in list
                if query.lower() in entry.lower():
                    entries_found.append(entry)
            # Return list of matches found
            return render(request, "encyclopedia/search.html",{
                "results": entries_found,
                "query": query,
                "form": SearchForm(),
            })

    # Default Values
    return render(request, "encyclopedia/search.html",{
        "results": "",
        "query": "",
        "form": SearchForm(),
    })

def create(request):
    if request.method == "POST":
        form = NewPageForm(request.POST) # Capturing the data entered by users.
        # Check if the provided data is valid
        if form.is_valid(): 
            title = form.cleaned_data["title"]
            data = form.cleaned_data["data"]
            # Check if the entry matches with the existing entries
            all_entries = util.list_entries()
            # If entry exists return the same page with error
            for entry in all_entries:
                if entry.lower() == title.lower():
                    return render(request, "encyclopedia/create.html",{
                        "form": SearchForm(),
                        "newPageForm": NewPageForm(),
                        "error": "That entry already exists",
                    })
            new_entry_title = "#" + title
            new_entry_data = "\n" + data
            new_entry_content = new_entry_title + new_entry_data    
            util.save_entry(title, new_entry_content)
            entry = util.get_entry(title)
            # Return the page for the newly created entry
            return render(request, "encyclopedia/entry.html",{
                "title": title,
                "entry": markdown2.markdown(entry),
                "form": SearchForm(),
                })
    # Default values
    return render(request, "encyclopedia/create.html",{
        "form": SearchForm(),
        "newPageForm": NewPageForm(),
    })

def edit(request, title):
    if request.method == "POST":
        # Get the data for the entry to be edited
        entry = util.get_entry(title)
        # Display content in textarea
        edit_form = EditPageForm(initial={'title': title, 'data': entry})
        # Return the page with forms filled with entry information
        return render(request, "encyclopedia/edit.html", {
            "form": SearchForm(),
            "editPageForm": edit_form,
            "title": title,
            "entry": entry,
            
        })

def submitEditEntry(request, title):
    if request.method == "POST":
        # Extract information from form
        edit_entry = EditPageForm(request.POST)
        if edit_entry.is_valid():
            # Extract 'data' from form
            content = edit_entry.cleaned_data["data"]
            # Extract 'title' from form
            title_edit = edit_entry.cleaned_data["title"]
            # if the title is edited, delete old file
            if title_edit != title:
                filename = f"entries/{title}.md"
                if default_storage.exists(filename):
                    default_storage.delete(filename)
            # Save new entry
            util.save_entry(title_edit, content)
            # Get the new entry
            entry = util.get_entry(title_edit)
            msg_success = "Successfully Updated!"
        # Return the edited entry
        return render(request, "encyclopedia/entry.html",{
            "title":title_edit,
            "entry": markdown2.markdown(entry),
            "form": SearchForm(),
            "msg_success": msg_success
        })

def randomEntry(request):
    # Get list of all entries
    entries = util.list_entries()
    # Get the title of a randomly selected entry
    title = random.choice(entries)
    # Return the redirect page for the entry
    return HttpResponseRedirect(reverse("encyclopedia:entry", args=[title]))
    








