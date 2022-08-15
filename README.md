# AWS Scanner

## Requirements
- AWS Account with AWS Config resource enabled.

## Instructions
1. Install dependencies 
    ```
    pip install requirements.txt
    ```
2. Create a file named ".env.yaml" following the ".env.example.yaml".
3. Replace the values with access key, secret key and session key (for SSO accounts).
4. Run.
    ```
    python3 scanner.py
    ```

## Todo
- [ ] Filter option.
- [ ] File name as parameter.