--


Test comint


### **App Overview**

The application is a web‑based project management system built with Django. It lets authenticated users create and manage projects and items (such as tasks, sub‑projects, and activities) under those projects. The app provides rich functionality including inline editing, file uploads, and update tracking—all integrated into a responsive, Bootstrap‑based UI.

---

### **Core Functionality**

1. **User Authentication & Dashboard:**
   - **Authentication:** Users log in and log out using Django’s built‑in authentication system. A custom logout view supports both GET and POST requests.
   - **Dashboard:** The dashboard aggregates overall statistics (e.g., total open items, high-priority items, overdue items) and displays a summary table for all projects with counts of open tasks, sub‑projects, and activities.

2. **Projects Management:**
   - **Project Creation:** Users can create new projects by filling out a form that includes the project name, description, a logo image, and contacts. Contacts are stored as a JSON field, and each contact can include details such as name, email, phone, and role.
   - **Project Editing & Deletion:** Users can update project information (including contacts) or delete projects. Deletion requires confirmation by re-entering the project name.
   - **Project Details:** The project details page displays the project’s name, description, contacts (shown horizontally), and separate tables for items grouped by type (tasks, sub‑projects, and activities). Each table includes columns for:
     - **Description**
     - **Created Date** (formatted using a custom filter)
     - **Due Date**
     - **Status** and **Priority** (with sorting links)
     - **Next Step Owner** (with inline editing via JavaScript and AJAX)
     - **Last Update** (displaying the timestamp in a custom format, for example “01-Jan-25 13H00”)
     - **Last Update Text** (the comment from the most recent update)
   - An **Export** button (placeholder) is also included on the project details page.

3. **Items Management:**
   - **Item Creation:** Under each project, users can create new items. Items can be one of three types: task, sub‑project, or activity. An optional GET parameter preselects the item type.
   - **Item Editing:** The item edit page allows users to update the main item fields (such as description, due date, status, priority, owner, next step owner) and add a new update that can include a comment and file upload. Existing updates (with files) are displayed in a table, and users can delete individual files from updates.
   - **Inline Editing:** On the project details page, the “Next Step Owner” field can be edited inline. When a user clicks the pencil icon, the field turns into an input; the new value is saved via an AJAX POST request to a dedicated API endpoint.

4. **Sorting:**
   - Users can sort items in the project details tables by status or priority. Header links add GET parameters (e.g. `?sort=status`), and the view orders the querysets accordingly.

---

### **File Structure**

- **core/models.py**  
  Contains two models:  
  - `Project` – stores project information (name, description, contacts, logo).  
  - `Item` – represents an item in a project (task, sub‑project, or activity) with fields for description, created date, due date, status, priority, owner, next step owner, and updates (stored as JSON).

- **core/forms.py**  
  Defines forms for creating and editing projects (`ProjectForm`) and items (`ItemForm`).

- **core/views.py**  
  Contains all view functions handling:
  - Dashboard, project list, project detail, project create, project edit, project delete.
  - Item create and item edit, including logic for adding updates with file uploads.
  - Inline update of the next step owner (via an API endpoint) and views to delete an update or delete a file from an update.
  - Custom logout view.

- **core/templates/**  
  Contains HTML templates:
  - `base.html` – the main layout (includes Bootstrap, Font Awesome, night mode toggle, nav bar).
  - `project_detail.html` – displays project details, contacts, and items tables with sorting and inline editing.
  - `project_create.html`, `project_edit.html`, `project_list.html`, `project_delete.html` – handle various project CRUD operations.
  - `item_create.html` and `item_edit.html` – manage item creation and editing (including update history and file uploads).

- **core/templatetags/formatting.py**  
  Contains a custom template filter `format_iso` to format ISO date strings (e.g., converting them to “01-Jan-25 13H00”).

- **URLs:**  
  - **core/urls.py** includes URL patterns for all views (projects, items, and API endpoints).
  - **project_manager/urls.py** includes the main URL patterns and integrates the core app’s URLs.

---

### **Overall Logic**

- **User Interaction:**  
  Authenticated users manage projects and items via a responsive web interface. The app uses Django messages for feedback and inline AJAX for a smoother user experience (for example, inline editing of the next step owner).

- **Data Management:**  
  Projects and items are stored in a relational database (with JSON fields for dynamic contact and update data). Updates (comments and file attachments) are stored as JSON arrays within each item.

- **Customization & Extensibility:**  
  The app is structured to allow easy expansion—for example, adding new item types, additional tabs (like Adoption), or export functionality in the future.

---

