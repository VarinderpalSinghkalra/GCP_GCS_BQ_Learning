.sh                                         
#!/usr/bin/env bash                         
set -e                                      
                                            
source "$1"  # Load config file             
                                            
echo "Using Project: $PROJECT_ID"           
                                            
# Create Project if not exists              
if gcloud projects describe "$PROJECT_ID" >/
dev/null 2>&1; then                         
  echo "Project already exists."            
else                                        
  echo "Creating Project..."                
  gcloud projects create "$PROJECT_ID"      
fi                                          
                                            
# Link Billing                              
echo "Linking Billing..."                   
gcloud beta billing projects link "$PROJECT_
ID" \                                       
  --billing-account="$BILLING_ACCOUNT"      
                                            
# Set defaults                              
gcloud config set project "$PROJECT_ID"     
gcloud config set compute/region "$DEFAULT_R
EGION"                                      
gcloud config set compute/zone "$DEFAULT_ZON
E"                                          
                                            
# Enable required APIs                      
echo "Enabling APIs..."                     
for api in "${APIS[@]}"; do                 
  gcloud services enable "$api"             
done                                        
                                            
echo "Setup Completed!"                     
``                     