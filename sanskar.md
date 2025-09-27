# Backend Lead, Database Administrator, Federated Engine Architect Tasks

This document outlines your specific tasks based on the corrected distributed architecture.

### Technology Stack:
- **Python**
- **Django**
- **PostgreSQL**

---

## Weeks 1-6: Foundation (COMPLETE)

### Recap:
- You have a working Django backend with a populated PostgreSQL database and a document API.
- Your system is the **primary data source**.

---

## Week 7: Configure for Remote Access

### Goal:
Allow your partner's applications (both his React frontend and his future Flask API) to connect to your PostgreSQL database over the network.

### Tasks:

1. **Locate Config Files:**
   - Find the following configuration files in your PostgreSQL data directory (e.g., `C:\Program Files\PostgreSQL\<VERSION>\data\`):
     - `postgresql.conf`
     - `pg_hba.conf`

2. **Edit `postgresql.conf`:**
   - Change:
     ```conf
     listen_addresses = 'localhost'
     ```
     to:
     ```conf
     listen_addresses = '*'
     ```

3. **Edit `pg_hba.conf`:**
   - Add a new line at the bottom to allow your partner's IP address to connect. You will need to ask your partner for his local IP.
     ```conf
     # TYPE  DATABASE    USER      ADDRESS                          METHOD
     host    all         all       <YOUR_PARTNER_IP_ADDRESS>/32      md5
     ```

4. **Restart PostgreSQL Server:**
   - Use the "Services" app in Windows to restart the PostgreSQL service.

5. **Configure Windows Firewall:**

   - Open "Windows Defender Firewall with Advanced Security".
   - Create a new "Inbound Rule":
     - **Rule Type:** Port
     - **Protocol and Ports:** TCP, Specific local ports: 5432
     - **Action:** Allow the connection
     - **Profile:** Keep all checked
     - **Name:** "PostgreSQL Project Access"

6. **Provide Connection Details:**
   - Give your partner your local IP address, PostgreSQL username, and password so he can test the connection.

---

## Week 8: Build the Query Decomposer

### Goal:
Build the initial version of the core query analysis and decomposition logic.

### Tasks:

1. **Work primarily in the `query_analyzer.py` script**:
   - Create a function that accepts a text query as input (e.g., "show me scholarships").

2. **Implement a simple keyword-based logic** to decide which data source to target:
   - **Keywords like** "job", "career" -> Target **Partner's Flask API**.
   - **Keywords like** "scholarship", "fund" -> Target **Partner's Flask API**.
   - **Keywords like** "document", "certificate" -> Target your own **Django API**.

3. **Output Example**:
   - Your script’s output should be a plan, such as:
     ```python
     {'target_api': 'http://<PARTNER_IP>:5000/api/scholarships'}
     ```

---

## Week 9: Implement Query Execution

### Goal:
Enhance the analyzer to execute the query plan.

### Tasks:

1. **Enhance the `query_analyzer.py` script**:
   - Add logic to use a library like `requests` to make an actual API call to the target URL identified in Week 8.

2. **Create a new endpoint in your Django application**:
   - Endpoint: `/api/federated-query/`
   - This endpoint should:
     - Receive a query from the frontend.
     - Run your `query_analyzer.py` script.
     - Return the final result (e.g., from your Django API or your partner's Flask API).

---

This document outlines your tasks and provides a structured approach to ensure that all backend responsibilities are met for the project. Let me know if you'd like to adjust anything or add more details!
