`1.2.2`
-------
Bug Fixes:
	- Fixed issue from last update for not importing scanned vouchers.
	- Fixed fik_payment_code was not added.

`1.2.1`
-------
New Version:
	- Released Odoo 8. 

Improvements:
	- Better looking upload view.

Bug Fixes:
	- Fixed issue for uploading too small images. This will now be shown in the voucher error message.


`1.2.0`
-------
New Features:
	- Added Upload App (Invoice Scan) to handle uploads. This makes it easier to handle uploads with mobile phones.
	- Foreward email is now determined by a self configured Odoo email.

Improvements:
	- Changed the configuration to be handled by the Upload App (Invoice Scan), except for activation.
	- Changed the Voucher report to be shown under the Upload App (Invoice Scan).
	- Simplified the Voucher state to only contain one state. Makes it easier to know the state of the voucher.
	- Make the Voucher view easier to overview.
	- Made the module compatible with the Purchase Order Matching module.

Bug Fixes:
	- Fixed case sensitive VAT matching


`1.1.1`
-------
New Features:
	- Possible to delete invoice and re-create it from the scanned voucher.

Improvements:
	- Made better system logging to avoid the system log to be spammed.
	- Apply default description for scanned invoice lines without descriptions.

Bug Fixes:
	- Prevent import failure if the scan engine adds new fields.


`1.1.0`
-------
New Versions:
	- Released Odoo 9 and 13. 

New Features:
	- Possible to add a default analytic account on the vendor bill lines.
	- Added functionality that rematch partner and trigger auto applying lines.
	- New setting-view under partners. Added a page-tab with settings only for invoice scan.
	- Extra features to automation has been applied.
	- Possible to convert the vendor bill to a credit note.
	- Adds scanned lines as default.

Improvements:
	- Added new scanned fields from scan engine.
	- Optimized the way scanned lines is added to the vendor bill.
	- Applied fallback account_id and tax for single lines.
	- Changed the voucher references values.
	- Optimized configuration of the API.

Bug Fixes:
	- Fixed issue for not validating with the correct company.
	- Fixed issue adding wrong account id.
	- Corrected tax methods.
	- Fixed issue for Odoo vendor bill upload (Odoo 12 and 13).


`1.0.16`
-------
Improvements:
	- Improved the selection of vendor to only look at suppliers.


Bug Fixes:
	- Fixed issue for not getting scanned vouchers with empty dates.


`1.0.15`
-------
New Features:
	- Added the ability to change company within a vendor bill or by multi selection.


`1.0.14`
-------
Improvements:
	- Improved the selection of vendor.

Bug Fixes:
	- Fixed issue for setting empty values for scanned vouchers. This will ensure correct update of scanned values.


`1.0.13`
-------
New Features:
	- Default tax from partner will now apply as default on every new invoice line.

Bug Fixes:
	- Fixed issue for creating invoices for multi company setup.


`1.0.12`
-------
Bug Fixes:
	- Fixed issue with auto validate single line. If no net amount it will take gross amount.
	- Fixed minor issue with the Danish FIK apply.
	- Fixed minor issue with Property fields.


`1.0.11`
-------
Bug Fixes:
	- Fixed issue with taxes not applied to the auto generated invoice line.


`1.0.10`
-------
New Features:
	- Apply scanned lines automatic to vendor bill.
	- Auto validate vendor bill if control value is 0.
	- Auto generate one invoice line from totals and apply it to the vendor bill.
	- Added refresh button on voucher report. Used to update voucher data.

Bug Fixes:
	- Minor bug fixes.
