Accounts and Permissions
========================

This section will detail basic processing concerning user accounts and permissions.

User Addition
--------------

1. Users submit a request for access through the website using their email, and an account is registered for them automatically.
2. If approved by an admin, an AWS IAM account is created and associated with the user.

  1. *Users must be also associated with a group, which determine their access to analyses.*
  2. Users' AWS credential request status is designated as 'Completed,' 'Pending,' or 'Denied.' Currently the user is unable to view this designation.
  
3. Users then use these IAM credentials to login to the site and perform analyses

  1. Users may also optionally add their name to their account details.

Potential Improvements (Jack's opinions)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* Automated IAM creation and association with user (only a checkbox approval form and association with group required by admin).
* Force users to login using their email and a password. Currently users are identified by their email, their IAM is identified by username, however they login using AWS access keys.
  I believe this workflow could be simplified if users created an account, and signed in with their email and password, and were able to check profile details and the status of their AWS credential request
  from this profile page. Once the user is given an IAM and gains access to the analyses, the IAM associated with the user account can be used for processing, and users don't need to store their own access keys.
* Remove the unused and extraneous views, variables, and functions.
* Automatically delete users who have been denied access after a time interval (so they can see in their profile that they were denied). 

User Permissions
----------------

Coming soon...
