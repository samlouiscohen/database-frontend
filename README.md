# database-frontend

The PostgreSQL account: slc2206

Web application URL: 

Compare / Contrast to original proposal: 
Our intial vision was that the user would be able to query the database with variety of fields 
to draw upon relevant information. One such query could be for a movie name and associated entities 
that we will allow them to choose from (drop down). For example, they may choose a specific movie 
name and then choose distributor: this will display the movie name and underneath all associated 
distributors. We did end up implementing this so that users could access that data. Instead of allowing them to select from a drop down menu, they have three routes to choose from:
- Movie info is for information relating to a specific movie
- Contributor info is for information relating to a specific contributor (actor/producer)
- Quick Qs is for information from comparing instances of the same entity (ex. which studio was founded first) 

Parts we did not end up implementing: 
We did not end up implementing the front end so the user had the ability to query the database with a variety of drop down fields, of thier choice. Instead we decided to go with three routes that provided access to a majority of the possible information a user would ever ask. This way the user did not need to know as much logic to get to the answers of thier question, which simplified the user experience. 

New features we added:
User Critic Reviews Page: We added the ability for users to submit thier own user reviews of movies already in the database. They enter thier name, age, gender, movie name, and thier rating. Once submitted the user critic reviews table automatically updates with thier new review. 


Most interesting web pages (in terms of database operations, what the pages are used for, how the page is related to the database operations):

1. User Critic Reviews Page:
As described above, this page allows users to submit thier own movie reviews. This is interesting becasue it allows the user to add new information to the database, via insertions of thier reviews. This is so cool because it means our database is no longer static but can evolve as more users interact with it. 

2. Quick Q's Page:
This page allows for users to select what entity they have questions about, and which specific attribute of that entity is of interest. Depending on the attribute, there may be options to rank in descending or ascending order. Then it displays a table of that entity's instances (for example, all the Distributors), ordered by the attribute the user chose. This is interesting because the user has the most freedom in this section to define the search. The database operations happening on the backend are a variety of queries that change depending on what entity and entity attributes the user selects. 
