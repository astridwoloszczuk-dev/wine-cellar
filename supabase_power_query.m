let
    BaseUrl = "https://mezayharkjyvnnhvdlww.supabase.co/rest/v1/wines?select=*&order=id",
    ApiKey = "PASTE_YOUR_KEY_HERE",
    Options = [Headers = [apikey = ApiKey, Authorization = "Bearer " & ApiKey]],

    Page1 = Json.Document(Web.Contents(BaseUrl & "&limit=1000&offset=0", Options)),
    Page2 = Json.Document(Web.Contents(BaseUrl & "&limit=1000&offset=1000", Options)),

    Combined = List.Combine({Page1, Page2}),
    AsTable = Table.FromList(Combined, Splitter.SplitByNothing()),
    Expanded = Table.ExpandRecordColumn(AsTable, "Column1", {
        "id", "name", "category", "sub_region", "vintage",
        "merchant", "storage_location",
        "bottle_count", "bottle_format",
        "cost_per_bottle", "value_per_bottle",
        "window_start", "window_mid", "window_end",
        "urgency", "status",
        "invoice_no", "paid", "notes",
        "sold_at", "sold_price_per_bottle", "sold_via",
        "created_at", "updated_at"
    })
in
    Expanded
