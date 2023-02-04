from flask import Flask, render_template, request, jsonify
import json
import pymysql
import sqlite3

app = Flask(__name__)

score = 0


# Creating a flask application.

@app.route("/", methods=['GET', 'POST'])
def index():
  if request.method == "POST":
    Gender = request.form['Yes_no_gender']
    age = request.form.get("age")
    tc = request.form.get("Cholestrol")
    systolic_bp = request.form.get("Systolic_blood_pressure")
    hdl = request.form.get("HDLCholestrol")
    diastolic_bp = request.form.get("Diastolic_blood_pressure")
    try:
      diabetes = request.form['Yes_no_D']
    except:
      diabetes = 'no'
    smoking = request.form['Yes_no_S']
    score = getPointstoRisk(Gender, age, tc, hdl, systolic_bp, diastolic_bp,
                            diabetes, smoking)
    comment = getRiskCategory(score)
    if (comment == "high risk"):
      color = "color:red;"
    elif (comment == "moderate risk"):
      color = "color:orange;"
    elif (comment == "low risk"):
      color = "color:lightgreen;"
    elif (comment == "very low risk"):
      color = "color:green;"
    suggestion = getSuggestion(comment)
    return render_template("index.html", var=1, score=score, comment=comment,
                           color=color, suggestion=suggestion)
  return render_template("index.html")


@app.route("/greek.html", methods=['GET', 'POST'])
def greek():
  if request.method == "POST":
    Gender = request.form['Yes_no_gender']
    print(Gender)
    age = request.form.get("age")
    print(age)
    tc = request.form.get("Cholestrol")
    print(tc)
    smoking = request.form['Yes_no_S']
    print(smoking)
    systolic_bp = request.form.get("Systolic_blood_pressure")
    print(systolic_bp)
    score = getGreekRisk(Gender, smoking, age, systolic_bp, tc)
    comment = getRiskCategory(score)
    if (comment == "high risk"):
      color = "color:red;"
    elif (comment == "moderate risk"):
      color = "color:orange;"
    elif (comment == "low risk"):
      color = "color:lightgreen;"
    elif (comment == "very low risk"):
      color = "color:green;"
    suggestion = getSuggestion(comment)
    return render_template("greek.html", var=1, score=score, comment=comment,
                           color=color, suggestion=suggestion)
  return render_template("greek.html")


def getAgePoints(Gender, age, cur):
  if (age == None):
    return 0
  sql = """
    SELECT """ + Gender.title() + """ FROM Age_chart
    Where """ + str(age) + """ BETWEEN Age_low AND Age_high;
    """
  cur.execute(sql)
  age_pointer = cur.fetchall()
  if (age_pointer == []):
    return 0
  age_pointer = age_pointer[0][0]
  return age_pointer


def getSmokingPoints(Gender, smoking, cur):
  sql = """
    SELECT """ + Gender.title() + """ FROM Smoking_chart
    WHERE Smoking == """ + "\"" + smoking.title() + "\"" + """ ;
    """
  cur.execute(sql)
  smoking_pointer = cur.fetchall()
  smoking_pointer = smoking_pointer[0][0]
  return smoking_pointer


def getDiabetesPoints(Gender, diabetes, cur):
  sql = """
    SELECT """ + Gender.title() + """ FROM Diabetes_chart
    WHERE Diabetes == """ + "\"" + diabetes.title() + "\"" + """ ;
    """
  cur.execute(sql)
  diabetes_pointer = cur.fetchall()
  diabetes_pointer = diabetes_pointer[0][0]
  return diabetes_pointer


def getBPPoints(Gender, systolic_bp, diastolic_bp, cur):
  if (systolic_bp == None or diastolic_bp == None):
    return 0
  sql = """
    SELECT """ + Gender.title() + """ FROM BP_chart
    Where """ + str(systolic_bp) + """ BETWEEN Systolic_BP_low AND Systolic_BP_high
    AND """ + str(diastolic_bp) + """ BETWEEN Diastolic_BP_low AND Diastolic_BP_high;
    """
  cur.execute(sql)
  bp_pointer = cur.fetchall()
  if (bp_pointer == []):
    return 0
  bp_pointer = bp_pointer[0][0]
  return bp_pointer


def getHDLPoints(Gender, hdl, cur):
  if (hdl == None):
    return 0
  sql = """
    SELECT """ + Gender.title() + """ FROM HDLCholesterol_chart
    Where """ + str(hdl) + """ BETWEEN HDL_low AND HDL_high;
    """
  cur.execute(sql)
  hdl_pointer = cur.fetchall()
  if (hdl_pointer == []):
    return 0
  hdl_pointer = hdl_pointer[0][0]
  return hdl_pointer


def getTCPoints(Gender, tc, cur):
  sql = """
    SELECT """ + Gender.title() + """ FROM TC_chart
    Where """ + str(tc) + """ BETWEEN Cholesterol_low AND Cholesterol_high;
    """
  cur.execute(sql)
  tc_pointer = cur.fetchall()
  if (tc_pointer == []):
    return 0
  tc_pointer = tc_pointer[0][0]
  return tc_pointer


def getPointstoRisk(Gender, age, tc, hdl, systolic_bp, diastolic_bp, diabetes,
    smoking):
  conn = sqlite3.connect("main.db")
  cur = conn.cursor()
  try:
    total_score = getAgePoints(Gender, age, cur) \
                  + getTCPoints(Gender, tc, cur) \
                  + getHDLPoints(Gender, hdl, cur) \
                  + getBPPoints(Gender, systolic_bp, diastolic_bp, cur) \
                  + getDiabetesPoints(Gender, diabetes, cur) \
                  + getSmokingPoints(Gender, smoking, cur)
  except:
    total_score = 0
  sql = """
    SELECT """ + Gender.title() + """Risk FROM PointsToScore_chart
    Where TotalScore == """ + str(total_score) + """;
    """
  cur.execute(sql)
  pts_pointer = cur.fetchall()
  conn.close()
  pts_pointer = pts_pointer[0][0]
  return pts_pointer


def getRiskCategory(pts_pointer):
  conn = sqlite3.connect("main.db")
  cur = conn.cursor()

  sql = """
    SELECT Category FROM RiskCategory_chart
    Where """ + str(pts_pointer) + """ BETWEEN Risk_low AND Risk_high;
    """
  cur.execute(sql)
  rc_pointer = cur.fetchall()
  conn.close()
  rc_pointer = rc_pointer[0][0]
  return rc_pointer


def getGreekRisk(Gender, smoking, age, systolic_bp, tc_greek):
  conn = sqlite3.connect("main.db")
  cur = conn.cursor()
  sql = """
    SELECT Risk FROM GreekDataSet_chart
    Where Gender == """ + "\"" + Gender.lower() + "\"" + """
    AND Smoking == """ + "\"" + smoking.title() + "\"" + """
    AND """ + str(age) + """ BETWEEN Age_low AND Age_high
    AND """ + str(systolic_bp) + """ BETWEEN Systolic_BP_low AND Systolic_BP_high
    AND """ + str(tc_greek) + """ BETWEEN TC_low AND TC_high;
    """
  cur.execute(sql)
  gr_pointer = cur.fetchall()
  conn.close()
  gr_pointer = gr_pointer[0][0]
  return gr_pointer

def getSuggestion(riskCategory):
  conn = sqlite3.connect("main.db")
  cur = conn.cursor()

  sql = """
  SELECT suggestion FROM Suggestion_chart
  Where category == """+"\""+riskCategory.lower()+"\""+""";
  """
  cur.execute(sql)
  rc_pointer = cur.fetchall()
  conn.close()
  rc_pointer = rc_pointer[0][0]
  return rc_pointer

if __name__ == "__main__":
  app.run(debug=True)
