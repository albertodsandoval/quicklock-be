# Authentication Endpoints
QuickLock backend handles authentication and authorization using *mostly* default **Django Rest Framework** (DRF) auth endpoints.

## Register User
`auth/register_user/`<br>

This endpoint enables registration for both normal users and administrator users (lock owners). The serializer is as follows:

* email - Required *string*
* 
