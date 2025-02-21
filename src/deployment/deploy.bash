zip -r lambda_function.zip lambda_function.py src/
aws lambda update-function-code --function-name calculate_mlb_rankings --zip-file fileb://lambda_function.zip --no-cli-pager
rm -rf package lambda_function.zip


aws lambda get-function --function-name calculate_mlb_rankings --no-cli-pager