import json
import requests
import smtplib
import datetime
import sys

# 1. Graceful Exit on File Not Found
try:
    with open('userDatabase.json', 'r') as file:
        data = json.load(file)
except FileNotFoundError:
    print("Error: The file 'userDatabase.json' was not found.")
    sys.exit(1) # Stop execution to prevent a NameError later

def check_aqi(city):
    # Security Note: It is best practice to store API keys in environment variables (.env)
    api_key = "0d48c30d9f8671d47ff1f07848407b242103390a"
    url = f"http://api.waqi.info/feed/{city}/?token={api_key}"
    try:
        response = requests.get(url)
        response.raise_for_status() # Check for HTTP errors
        json_file = response.json()
        if json_file["status"] == "ok":
            return json_file["data"]["aqi"]
        else:
            print("Error: Failed to retrieve AQI data.")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Network error occurred: {e}")
        return None

# Get data for user "ABC"
user = data["ABC"]
aqi_level = check_aqi(user["city"])

# 2. Prevent NoneType crash by wrapping the rest of the logic
if aqi_level is not None:
    # --- PROACTIVE TRIGGER LOGIC ---
    alert_messages = []
    diseased = False

    # 1. Asthma / COPD
    if user.get("asthma") == True and aqi_level > 51:
        alert_messages.append("Preventive: Lower air quality detected. Keep rescue inhaler nearby; avoid uphill walking.")
        diseased = True
        
    # 2. Pregnancy
    if user.get("pregnant") == True and aqi_level > 51:
        alert_messages.append("Protective: Prioritize indoor air today. Air quality is shifting toward unhealthy levels.")
        diseased = True

    # 3. Heart & Lung Disease
    if user["healthConditions"].get("heartDisease") == True and aqi_level > 101:
        alert_messages.append("Vital-Based: Pollution levels may strain heart health. Avoid heavy lifting or outdoor HIIT.")
        diseased = True

    if user["healthConditions"].get("lungDisease") == True and aqi_level > 51:
        alert_messages.append("Respiratory: Protect your lungs today. Avoid prolonged outdoor exertion.")
        diseased = True

    # 4. Diabetes
    if user["healthConditions"].get("diabetes") == True and aqi_level > 101:
        alert_messages.append("Monitoring: Air pollution can affect glucose levels. Monitor your readings closely today.")
        diseased = True

    # 5. Skin / Eczema
    if user["healthConditions"].get("eczema") == True and aqi_level > 101:
        alert_messages.append("Topical: High pollution levels detected. Consider a barrier cream before heading out to protect skin.")
        diseased = True

    # 6. Neurological
    if user["healthConditions"].get("neurological") == True and aqi_level > 151:
        alert_messages.append("Wellness: High particulates can impact focus and energy. Consider a low-stimulation indoor environment.")
        diseased = True

    # 7. Autoimmune
    if user["healthConditions"].get("autoimmune") == True and aqi_level > 101:
        alert_messages.append("Energy Management: Poor air quality may trigger inflammation. Schedule extra rest periods today.")
        diseased = True

    # 8. Kidney Disease
    if user["healthConditions"].get("kidneyDisease") == True and aqi_level > 151:
        alert_messages.append("Hydration-Focus: Poor air quality detected. Stay well-hydrated to help your body process toxins.")
        diseased = True

    # 9. Allergies (Pollen/Dust)
    if (user["allergies"].get("pollen") == True or user["allergies"].get("dust") == True) and aqi_level > 50:
        alert_messages.append("Behavioral: High particle/dust levels detected. Keep windows closed and shower after being outdoors.")
        diseased = True
    
    if not diseased and aqi_level > 151:
        alert_messages.append("General: AQI has reached hazardous levels. Limit outdoor activities and follow local health advisories.")
        
    # --- EVALUATE TRIGGERS ---
    # 3. Fix logic bug by storing the trigger state clearly
    aqi_changed_significantly = abs(aqi_level - data["metadata"]["previousAQI"]) > 20
    
    try:
        last_triggered_str = data["metadata"].get("lastTriggered")
        last_triggered_time = datetime.datetime.fromisoformat(last_triggered_str) if last_triggered_str else datetime.datetime.min
    except (ValueError, TypeError):
        last_triggered_time = datetime.datetime.min
    time_elapsed = (datetime.datetime.now() - last_triggered_time).total_seconds() > 86400
    
    should_trigger = aqi_changed_significantly or time_elapsed

    # Update JSON only if we are actually triggering
    if should_trigger:
        data["metadata"]["trigger?"] = True
        data["metadata"]["lastTriggered"] = datetime.datetime.now().isoformat()
        data["metadata"]["previousAQI"] = aqi_level

        with open('userDatabase.json', 'w') as file:
            json.dump(data, file, indent=4)
    else:
        # Ensure it's set to False if conditions aren't met to prevent accidental emails
        data["metadata"]["trigger?"] = False
        with open('userDatabase.json', 'w') as file:
             json.dump(data, file, indent=4)

    # --- SEND THE EMAIL IF TRIGGERS WERE MET ---
    if len(alert_messages) > 0 and should_trigger:
        try:
            # Moved SMTP setup here so we don't log in unless we actually need to send an email
            email = "virthlitestsender@gmail.com" 
            receiver_email = user["email"]
            # Security Note: Best practice is to use os.environ.get("EMAIL_PASS")
            app_password = "vzyh bhlg oxeq majq"

            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(email, app_password)

            subject = f"Personalized Air Quality Alert (AQI: {aqi_level})"
            body = f"Hello,\n\nBased on your health profile and the current AQI of {aqi_level} in {user['city']}, here are your personalized advisories:\n\n"
            
            for msg in alert_messages:
                body += f"- {msg}\n"
                
            body += "\nStay safe!"
            
            # Sendmail requires a specific format for Subject + Body
            # Make sure there is a blank line separating headers from the body
            full_email_string = f"Subject: {subject}\n\n{body}"
            
            server.sendmail(email, receiver_email, full_email_string)
            print("Triggers met! Personalized email sent.")
            
        except Exception as e:
            print(f"Failed to send email: {e}")
        finally:
            # 4. Always ensure the server connection is closed
            if 'server' in locals():
                server.quit()
    else:
        if not should_trigger:
            print("Cooldown period active or AQI hasn't changed significantly. No email sent.")
        else:
            print("AQI is safe for the user's specific profile. No email sent.")

else:
    print("Execution aborted due to missing AQI data.")