import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from scipy.stats import chi2_contingency

from musclehub_project.codecademySQL import sql_query

pd.set_option('display.max_columns', None)
pd.set_option('display.expand_frame_repr', False)
pd.set_option('max_colwidth', None)

visits = sql_query("SELECT * FROM visits")
fitness = sql_query("SELECT * FROM fitness_tests")
applications = sql_query("SELECT * FROM applications")
purchases = sql_query("SELECT * FROM purchases")

visits_after_7 = visits[visits.visit_date >= "7-1-17"].reset_index()

visits_fitness = pd.merge(visits_after_7, fitness[["first_name", "last_name", "email", "fitness_test_date"]], how="left", on=["first_name", "last_name", "email"])
visits_fitness_applications = pd.merge(visits_fitness, applications[["first_name", "last_name", "email", "application_date"]], how="left", on=["first_name", "last_name", "email"])
df = pd.merge(visits_fitness_applications, purchases[["first_name", "last_name", "email", "purchase_date"]], how="left", on=["first_name", "last_name", "email"])
df.fillna(0, inplace=True)
df["ab_test_group"] = df.fitness_test_date.apply(lambda x: "A" if x else "B")
ab_counts = df.groupby(df.ab_test_group).index.count().reset_index()
ab_counts.columns = ["ab_test_group", "okok"]

plt.pie(list(ab_counts.okok), labels=["A", "B"], autopct='%1.3f%%',)
plt.axis('equal')

df["is_application"] = df.application_date.apply(lambda x: "Application" if x else "No Application")
app_counts = df.groupby([df.ab_test_group, df.is_application]).index.count().reset_index()

app_pivot = app_counts.pivot(index="ab_test_group", columns="is_application", values="index").reset_index()
app_pivot["Total"] = app_pivot["Application"] + app_pivot["No Application"]
app_pivot["Percent with Application"] = app_pivot["Application"] / app_pivot["Total"]

contingency = [
    [250, 2254],
    [325, 2175]
]
_, p_value, _, _ = chi2_contingency(contingency)
# result is significant

df["is_member"] = df.purchase_date.apply(lambda x: "Member" if x else "Not Member")
just_apps = df[df.is_application == "Application"]
just_apps_count = just_apps.groupby(["ab_test_group", "is_member"]).index.count().reset_index()
member_pivot = just_apps_count.pivot(index="ab_test_group", columns="is_member", values="index").reset_index()
member_pivot["Total"] = member_pivot["Member"] + member_pivot["Not Member"]
member_pivot["Percent Purchase"] = member_pivot["Member"] / member_pivot["Total"]

contingency_app = [
    [200, 50],
    [250, 75]
]
_, p_value2, _, _ = chi2_contingency(contingency_app)
# not significant

final_member = df.groupby(["ab_test_group", "is_member"]).index.count().reset_index()
final_member_pivot = final_member.pivot(index="ab_test_group", columns="is_member", values="index").reset_index()
final_member_pivot["Total"] = final_member_pivot["Member"]+final_member_pivot["Not Member"]
final_member_pivot["Percent Purchase"] = final_member_pivot["Member"] / final_member_pivot["Total"]


contingency_all = [
    [200, 2304],
    [250, 2250]
]

_, p_value3, _, _ = chi2_contingency(contingency_all)
# significant


app = list(app_pivot["Percent with Application"])
member = list(member_pivot["Percent Purchase"])
final_member_val = list(final_member_pivot["Percent Purchase"])

fig = plt.figure(figsize=(5, 10))

ax = plt.subplot(3,1,1)
ax.bar(range(len(app)), app)
ax.set_xticks(range(len(app)))
ax.set_xticklabels(["Group A", "Group B"])
ax.set_ylabel("Percent")
ax.set_title("Percent of visitors who apply")

ax2 = plt.subplot(3,1,2)
ax2.bar(range(len(member)), member)
ax2.set_xticks(range(len(member)))
ax2.set_xticklabels(["Group A", "Group B"])
ax2.set_ylabel("Percent")
ax2.set_title("Percent of applicants who purchase a membership")

ax3 = plt.subplot(3,1,3)
ax3.bar(range(len(final_member_val)), final_member_val)
ax3.set_xticks(range(len(final_member_val)))
ax3.set_xticklabels(["Group A", "Group B"])
ax3.set_ylabel("Percent")
ax3.set_title("Percent of visitors who purchase a membership")

plt.show()


if __name__ == "__main__":
    print(app_pivot)
    print(member_pivot)
    print(final_member_pivot)
    print(df)
