# 📖 Masterdex API Documentation

This document describes all available backend API routes for the Masterdex app.
All routes are prefixed with /api.

# Authentication Routes

## Login

  ### POST /api/auth/login
  **Authentication required:**  No  

  **Request body:**
  ```json
  {
    "email": "demo@aa.io",
    "password": "password"
  }
  ```
  Response:

  ```json
  {
    "id": 1,
    "username": "Demo",
    "email": "demo@aa.io"
  }
  ```

  ---

## Logout

  ### POST /api/auth/logout

  **Authentication required:**  Yes  

  **Description:** Logs out the current user by clearing the session.  

    **Response:**
    ```json
    {
      "message": "User logged out"
    }
    ```

  ---

## Signup 

  ### POST /api/auth/signup
  **Authentication required:** No  

  **Description:** Creates a new user account.  

  **Request Body:**

  ```json
  {
    "firstName": "Demo",
    "lastName": "User",
    "username": "demo",
    "email": "demo@aa.io",
    "password": "password"
  }
  ```

  **Response:**

  ```json
  {
    "id": 1,
    "firstName": "Demo",
    "lastName": "User",
    "username": "demo",
    "email": "demo@aa.io",
    "createdAt": "...",
    "updatedAt": "..."
  }
  ```

  ---

## Get Current User

  ### **GET /api/auth/**

  **Authentication required:** Yes

  **Description:** Returns the currently authenticated user if logged in.

  **Response:**

  ```json
  {
    "id": 1,
    "firstName": "Demo",
    "lastName": "User",
    "username": "demo",
    "email": "demo@aa.io",
    "createdAt": "...",
    "updatedAt": "..."
  }
  ```

---

# User Routes

## Get All Users

  ### **GET /api/users/**

  **Authentication Required:** Yes

  **Description:** Returns a list of all users in the database.

  **Response:**

  ```json
  {
    "users": [
      {
        "id": 1,
        "firstName": "Demo",
        "lastName": "User",
        "username": "demo",
        "email": "demo@aa.io",
        "createdAt": "...",
        "updatedAt": "..."
      },
      {
        "id": 2,
        "firstName": "Marnie",
        "lastName": "Smith",
        "username": "marnie",
        "email": "marnie@aa.io",
        "createdAt": "...",
        "updatedAt": "..."
      }
      ]
    }
  ```

  ---

## Get User By ID

  ### **GET /api/users/:id**

  **Authentication Required:** Yes

  **Description:** Returns a single user by using their ID.

  ## **Response: Upon Success**

  ```json
  {
    "user": {
      "id": 1,
      "firstName": "Demo",
      "lastName": "User",
      "username": "demo",
      "email": "demo@aa.io",
      "createdAt": "...",
      "updatedAt": "..."
    }
  }
  ```
  ## **Response: No User By Given ID**

  ```json
  {
    "errors": { "message": "User not found" }
  }
  ```

  ---

## Update/Edit User

  ### PUT/api/users/:id

  **Authentication Required:** Yes (Must be logged in as the user being edited)

  **Description:** Updates a user’s profile information.

  **Request Body:**

  ```json
  {
    "username": "newdemo",
    "email": "newdemo@aa.io",
    "first_name": "DemoUpdated",
    "last_name": "UserUpdated"
  }
  ```

  **Response: On Success**

  ```json
  {
    "user": {
      "id": 1,
      "firstName": "DemoUpdated",
      "lastName": "UserUpdated",
      "username": "newdemo",
      "email": "newdemo@aa.io",
      "createdAt": "...",
      "updatedAt": "..."
    }
  }
  ```

  **Response (unauthorized):**

  ```json
  {
    "errors": { "message": "Unauthorized" }
  }
  ```

  ---

## Delete User

  ### DELETE /api/users/:id

  **Auth required:** Yes (must be the logged-in user)

  **Description:** Deletes the user account permanently.

  **Response (success):**
  ```json
  {
    "message": "User deleted successfully"
  }
  ```


  **Response (unauthorized):**
  ```json
  {
    "errors": { "message": "Unauthorized" }
  }
  ```

---

# Follow Routes

## Get Followers of a User
  
  ### GET /api/follows/:user_id/followers

  **Auth required:** Yes

  **Description:** Get a list of all followers of a given user.

  **Response:**

  ```json
  {
    "followers": [
      {
        "id": 2,
        "username": "marnie",
        "firstName": "Marnie",
        "lastName": "Smith"
      },
      {
        "id": 4,
        "username": "alice_tcg",
        "firstName": "Alice",
        "lastName": "Williams"
      }
    ]
  }
  ```

  ---

## Get Users a User is Following
  
  ### GET /api/follows/:user_id/following
  
  **Authentication required:** Yes

  **Description:** Get a list of all users that the given user is following.

  **Response:**

  ```json
  {
    "following": [
      {
        "id": 3,
        "username": "bobbie",
        "firstName": "Bobbie",
        "lastName": "Johnson"
      },
      {
        "id": 5,
        "username": "charlie_collector",
        "firstName": "Charlie",
        "lastName": "Brown"
      }
    ]
  }
  ```

## Follow a User

  ### POST /api/follows/:user_id

  **Auth required:** Yes  

  **Description:** Follow another user.  

  **Response (success):**
  ```json
  {
    "follow": {
      "id": 1,
      "followerId": 2,
      "followingId": 3,
      "createdAt": "...",
      "updatedAt": "..."
    }
  }
  ```

  **Response (cannot follow self):**
  ```json
  {
    "errors": { "message": "You cannot follow yourself" }
  }
  ```
  **Response (already following):**

  ```json
  {
    "errors": { "message": "Already following this user" }
  }
  ```

  ---

## Unfollow a User

  ### DELETE /api/follows/:user_id

  **Auth required:** Yes

  **Description:** Unfollow a user that the current user is following.

  **Response (success):**
  ```json
  {
    "message": "Unfollowed successfully"
  }
  ```

  **Response (not following):**
  ```json
  {
    "errors": { "message": "Not following this user" }
  }
  ```

  ---

---

# Binder Routes

## Get All Current User's Binders  

  ### **GET /api/binders**  

  **Authentication required:** Yes  

  **Description:** Returns all binders belonging to the logged-in user.  

  **Response:**  
  ```json
    {
      "binders": [
        {
          "id": 1,
          "name": "Demo's Favorite Cards",
          "description": "My most treasured Pokémon cards",
          "user_id": 2,
          "setId": "base1",
          "setName": "Base Set",
          "printedTotal": 102,
          "totalSetCards": 102
        }
      ]
    }
  ```

## Get a Single Binder

  ### GET /api/binders/:binder_id

  **Authentication required:** Yes

  **Description:** Returns a single binder with all of its cards.

  **Response:**
  ```json
  {
    "binder": {
      "id": 1,
      "name": "Demo's Favorite Cards",
      "description": "My most treasured Pokémon cards",
      "user_id": 2,
      "setId": "base1",
      "setName": "Base Set",
      "cards": [
        {
          "id": 10,
          "card_id": "base1-58",
          "name": "Pikachu",
          "rarity": "Common",
          "images": { "small": "...", "large": "..." }
        }
      ]
    }
  }
  ```

## Get Binder Progress

  ### GET /api/binders/:binder_id/progress

  **Authentication required:** Yes

  **Description:** Returns completion percentage for a binder’s set.

  **Response:**

  ```json
  {
    "binder_id": 1,
    "collected": 10,
    "total": 102,
    "progress": 9.8
  }
  ```

## Create Binder

  ### POST /api/binders

  **Authentication required:** Yes

  **Request Body:**
  ```json
  {
    "name": "My Binder",
    "description": "Water-type cards",
    "set_id": "base1",
    "set_name": "Base Set",
    "printed_total": 102,
    "total_in_set": 102
  }
  ```

  **Response:**
  ```json
  {
    "binder": {
      "id": 5,
      "name": "My Binder",
      "description": "Water-type cards",
      "user_id": 2,
      "setId": "base1",
      "setName": "Base Set"
    }
  }
  ```

## Update Binder
  
  ### PUT /api/binders/:binder_id

  **Authentication required:** Yes (must own the binder)

  **Request Body:**

  ```json
  {
    "name": "Updated Binder Name",
    "description": "Updated description"
  }
  ```
  **Response:**

  ```json
  {
    "id": 1,
    "name": "Updated Binder Name",
    "description": "Updated description",
    "user_id": 2,
    "setId": "base1",
    "setName": "Base Set"
  }
  ```

## Delete Binder

  ### DELETE /api/binders/:binder_id

  **Authentication required:** Yes (must own the binder)

  **Response:**

  ```json
  {
    "message": "Binder deleted successfully"
  }
  ```

---

# Card Routes (Inside Binders)

## Get Cards in Binder

  ### GET /api/binders/:binder_id/cards?page=1

  **Authentication required:** Yes

  **Description:** Get binder’s cards, paginated 9 per page.

  **Response:**

  ```json
  {
    "binder_id": 1,
    "page": 1,
    "per_page": 9,
    "total_cards": 25,
    "total_pages": 3,
    "cards": [
      {
        "id": 15,
        "card_id": "base1-4",
        "name": "Charizard",
        "rarity": "Rare Holo"
      }
    ]
  }
  ```

## Add Card to Binder

  ### POST /api/binders/:binder_id/add

  **Authentication required:** Yes

  **Request Body:**
  ```json
  {
    "card": {
      "id": "base1-4",
      "name": "Charizard",
      "supertype": "Pokémon",
      "hp": 120,
      "set": { "id": "base1", "name": "Base Set" },
      "number": "4",
      "rarity": "Rare Holo",
      "images": { "small": "...", "large": "..." }
    }
  }
  ```

  **Response:**
  ```json
  {
    "message": "Added Charizard to Demo's Favorite Cards"
  }
  ```

## Remove Card from Binder

  ### DELETE /api/binders/:binder_id/remove/:card_id

  **Authentication required:** Yes

  **Response:**

  ```json
  {
    "message": "Removed Charizard from Demo's Favorite Cards"
  }
  ```

---

# Card Routes (Utilizing TCG API V2)

## Search Cards  

  ### **GET /api/cards/search?q={query}&page={page}&pageSize={pageSize}**  

  **Authentication required:** No  

  **Description:** Searches the Pokémon TCG API for cards and returns paginated results.  

  **Query Parameters:**  
  - `q` (string, required): Pokémon TCG search query (e.g. `name:Pikachu`, `set.id:base1`).  
  - `page` (int, optional, default: 1): Page number of results.  
  - `pageSize` (int, optional, default: 20): Number of results per page.  

  **Example Request:**  
  ```http
  GET /api/cards/search?q=name:Pikachu&page=1&pageSize=5
  ```

  **Response (success):**
  ```json
  {
    "data": [
      {
        "id": "base1-58",
        "name": "Pikachu",
        "supertype": "Pokémon",
        "subtypes": ["Basic"],
        "hp": "40",
        "types": ["Lightning"],
        "set": {
          "id": "base1",
          "name": "Base Set",
          "series": "Base",
          "printedTotal": 102,
          "total": 102
        },
        "number": "58",
        "rarity": "Common",
        "images": {
          "small": "https://images.pokemontcg.io/base1/58.png",
          "large": "https://images.pokemontcg.io/base1/58_hires.png"
        }
      }
    ],
    "page": 1,
    "pageSize": 5,
    "count": 1,
    "totalCount": 1
  }
  ```

  **Response (error - missing query):**
  ```json
  {
    "errors": { "message": "Missing search query" }
  }
  ```

  **Response (error - external API issue):**

  ```json
  {
    "errors": { "message": "Failed to fetch cards" }
  }
  ```

---

# Comment Routes  

## Get All Comments for a Binder  

  ### **GET /api/binders/:binder_id/comments**  

  **Authentication required:** Yes  

  **Description:** Returns all comments for the given binder.  

  **Response:**  
  ```json
  [
    {
      "id": 1,
      "content": "Great collection!",
      "userId": 2,
      "binderId": 1,
      "createdAt": "...",
      "updatedAt": "...",
      "author": {
        "id": 2,
        "username": "marnie"
      }
    },
    {
      "id": 2,
      "content": "Love the holo cards.",
      "userId": 3,
      "binderId": 1,
      "createdAt": "...",
      "updatedAt": "...",
      "author": {
        "id": 3,
        "username": "bobbie"
      }
    }
  ]
  ```

## Add a Comment to a Binder

  # POST /api/binders/:binder_id/comments

  **Authentication required:** Yes

  **Description:** Adds a new comment to a binder. Users cannot comment on their own binder.

  **Request Body:**
  ```json
  {
    "content": "Awesome cards!"
  }
  ```

  **Response (success):**

  ```json
  {
    "id": 3,
    "content": "Awesome cards!",
    "userId": 2,
    "binderId": 1,
    "createdAt": "...",
    "updatedAt": "...",
    "author": {
      "id": 2,
      "username": "marnie"
    }
  }
  ```

  **Response (error - own binder):**
  ```json
  {
    "errors": { "message": "You cannot comment on your own binder" }
  }
  ```

  **Response (error - empty content):**
  ```json
  {
    "errors": { "message": "Content is required" }
  }
  ```

## Update a Comment
  
  # PUT /api/comments/:comment_id
  
  **Authentication required:** Yes (must be the author)

  **Description:** Updates the content of an existing comment.

  **Request Body:**
  ```json
  {
    "content": "Updated comment text"
  }
  ```

  **Response (success):**
  ```json
  {
    "id": 3,
    "content": "Updated comment text",
    "userId": 2,
    "binderId": 1,
    "createdAt": "...",
    "updatedAt": "...",
    "author": {
      "id": 2,
      "username": "marnie"
    }
  }
  ```

  **Response (unauthorized):**
  ```json
  {
    "errors": { "message": "Unauthorized" }
  }
  ```

## Delete a Comment

  ### DELETE /api/comments/:comment_id

  **Authentication required:** Yes (must be the author)

  **Description:** Deletes a comment.

  **Response (success):**
  ```json
  {
    "message": "Comment deleted successfully"
  }
  ```

  **Response (unauthorized):**
  ```json
  {
    "errors": { "message": "Unauthorized" }
  }
  ```

---

# Note:

  ### All routes return errors in this format:

  ```json
  { "errors": { "message": "Error description" } }
  ```