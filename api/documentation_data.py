doc_data = {
    "imports": {
        "summary": "Create or update list of items",
        "description":
            'Create or update a list of items with the id[str], url[str],'
            ' parentId[str], size[int], type["FOLDER" or "FILE"], updateDate[str]',
    },
    "delete": {
        "summary": "Delete an item by id and date",
        "description":
            'Delete an item by id, changes all dependent folders: set the date of removal',
    },
    "nodes": {
        "summary": "Find item",
        "description":
            'Get the item and all dependent items as a children',
    },
    "updates": {
        "summary": "Find activities in the last 24 hours",
        "description":
            'Find all items which activities was in the last 24 hours',
    }
}
