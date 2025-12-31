# Stock Transfer Views Implementation

1.  **transfer_list(request, branch_id)**:
    - Lists transfers where `source_branch` OR `destination_branch` matches `branch_id`.
    - Tabs for "Sent" and "Received".

2.  **transfer_create(request, branch_id)**:
    - Form to select `destination` and `notes`.
    - Dynamic JS to add products and quantities (similar to POS or Order form).
    - On POST:
        - Create `StockTransfer` (pending).
        - Create `StockTransferItem`s.
        - Deduct stock from source? (Usually happens on creation or final approval. Let's say deducted on creation to reserve it).

3.  **transfer_detail(request, branch_id, pk)**:
    - Shows status and items.
    - If `status == 'pending'` and user is in `destination_branch`: Show "Receive/Approve" button.

4.  **transfer_receive(request, branch_id, pk)**:
    - Updates status to `completed`.
    - Adds stock to destination branch.
