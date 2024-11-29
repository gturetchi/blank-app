import streamlit as st
import pymongo
import pandas as pd

vaccination_data_path = './daily-covid-19-vaccination-doses.csv'
global_data_path = './WHO-COVID-19-global-daily-data.csv'

vaccination_data = pd.read_csv(vaccination_data_path)
global_data = pd.read_csv(global_data_path)

# # URLs for the CSV files
# file_cases = './WHO-COVID-19-global-daily-data.csv'
# file_vaccin = './daily-covid-19-vaccination-doses.csv'

# # Load the CSV files directly from the URLs into Pandas DataFrames
# cases_df = pd.read_csv(file_cases)
# vaccin_df = pd.read_csv(file_vaccin)

# # Connect to MongoDB
# db = client['covid']

# # Import cases data into MongoDB
# cases_collection = db['case']
# cases_data = cases_df.to_dict(orient='records')
# cases_collection.insert_many(cases_data)

# # Import vaccination data into MongoDB
# vaccin_collection = db['vaccin']
# vaccin_data = vaccin_df.to_dict(orient='records')
# vaccin_collection.insert_many(vaccin_data)


# client = pymongo.MongoClient(connection_string)
mongodb_connection_string = st.secrets["mongodb"]["connection_string"]

@st.cache_resource
def init_connection():
    return pymongo.MongoClient(mongodb_connection_string)

client = init_connection()

# db = client['covid']
# collection = db['case']

# def display_documents():
#     documents = collection.find().limit(5)
#     for doc in documents:
#         st.write(doc)

# @st.cache_data(ttl=600)
# def get_data():
#     db = client.abc
#     items = db.mycollection.find()
#     items = list(items) 
#     return items

# items = get_data()

# display_documents()

st.image("img/qr.png")

st.title("🎈 Impactul vaccinării împotriva COVID-19 in Republica Moldova")

st.subheader("De unde date ?")
st.write(""" 
De aici 👉 https://data.who.int/dashboards/covid19/cases?n=c
""")

st.subheader("Ce date avem ?")
st.write(""" 	
         1. Country: Numele țării. 
         2. New_cases: Numărul de cazuri noi raportate în ziua respectivă (poate avea valori lipsă).
         3. Cumulative_cases: Numărul total de cazuri raportate până la acea dată.
         4. New_deaths: Numărul de decese noi raportate (poate avea valori lipsă).
         5. Cumulative_deaths: Numărul total de decese raportate până la acea dată.
         6. Entity: Numele țării sau al regiunii.	
         7. Day: Data.
         8. COVID-19 doses (daily, 7-day average): Numărul mediu zilnic de doze administrate (medie pe 7 zile).
""")

st.write("""
    Probleme:

	1. Rata de vaccinare în Moldova: Care sunt tendințele în rata zilnică de vaccinare în Republica Moldova de la începutul campaniei de vaccinare?
	2. Impactul vaccinării asupra numărului de cazuri noi: Există o corelație între creșterea ratelor de vaccinare și scăderea numărului de cazuri noi în Moldova?
	3. Impactul cumulativ al vaccinării asupra numărului total de cazuri și decese: Cum a influențat numărul cumulat de doze administrate rata cazurilor și deceselor cumulative în Republica Moldova?
	4. Eficiența vaccinării asupra mortalității: Cum a influențat vaccinarea mortalitatea în Moldova?
	5. Comparația internațională: Cum se compară ratele de vaccinare și impactul lor în Moldova cu alte țări similare din regiune?

Ipoteze pentru analiză:

	Y1: Rata de vaccinare în Moldova are o tendință crescătoare stabilă pe parcursul anului 2021.
	Y2: O creștere a ratelor de vaccinare este asociată cu o scădere semnificativă a cazurilor noi în Moldova.
	Y3: O creștere a numărului total de doze administrate este asociată cu o rată mai scăzută de creștere a cazurilor și deceselor cumulative în Republica Moldova.
	Y4: Mortalitatea cauzată de COVID-19 scade proporțional cu creșterea ratei de vaccinare în Moldova.
	Y5: Moldova are rate de vaccinare mai scăzute decât media regiunii, dar impactul vaccinării este similar în ceea ce privește reducerea cazurilor și a mortalității.
""")

#########################
st.write("Y1: Rata de vaccinare în Moldova are o tendință crescătoare stabilă pe parcursul anului 2021.")


moldova_vaccination_data = vaccination_data[vaccination_data['Entity'] == 'Moldova']
moldova_vaccination_data['Day'] = pd.to_datetime(moldova_vaccination_data['Day'])
moldova_daily_vaccinations = moldova_vaccination_data.groupby('Day')['COVID-19 doses (daily, 7-day average)'].sum()


import matplotlib.pyplot as plt

plt.figure(figsize=(12, 6))
plt.plot(moldova_daily_vaccinations.index, moldova_daily_vaccinations.values, label='Vaccination Rate (7-day average)', color='blue')
plt.title("Tendința zilnică a vaccinării în Republica Moldova (7-day average)")
plt.xlabel("Date")
plt.ylabel("Număr doze administrate (7-day average)")
plt.axhline(y=moldova_daily_vaccinations.mean(), color='green', linestyle='--', label=f"Media: {moldova_daily_vaccinations.mean():.2f}")
plt.legend()
plt.grid(True)
plt.show()

st.pyplot(plt)

st.image("img/covid_news.png")
#########################

#########################
st.write("Y2: O creștere a ratelor de vaccinare este asociată cu o scădere semnificativă a cazurilor noi în Moldova.")

moldova_global_data = global_data[global_data['Country'] == 'Republic of Moldova']

moldova_global_data['Date_reported'] = pd.to_datetime(moldova_global_data['Date_reported'])

merged_data = pd.merge(
    moldova_global_data,
    moldova_vaccination_data,
    left_on='Date_reported',
    right_on='Day',
    how='inner'
)

merged_data = merged_data[['Date_reported', 'COVID-19 doses (daily, 7-day average)', 'New_cases']].dropna()

correlation = merged_data['COVID-19 doses (daily, 7-day average)'].corr(merged_data['New_cases'])

fig, ax1 = plt.subplots(figsize=(14, 7))


ax1.plot(
    merged_data['Date_reported'],
    merged_data['COVID-19 doses (daily, 7-day average)'],
    label="Vaccination Rate (7-day average)",
    color='blue'
)
ax1.set_xlabel("Date")
ax1.set_ylabel("Vaccination Rate", color='blue')
ax1.tick_params(axis='y', labelcolor='blue')
ax1.legend(loc="upper left")

ax2 = ax1.twinx()
ax2.plot(
    merged_data['Date_reported'],
    merged_data['New_cases'],
    label="New Cases",
    color='red'
)
ax2.set_ylabel("New Cases", color='red')
ax2.tick_params(axis='y', labelcolor='red')
ax2.legend(loc="upper right")

plt.title("Relația dintre rata de vaccinare și numărul de cazuri noi în Republica Moldova")
plt.grid()
plt.show()

st.pyplot(plt)

lags = [15, 30, 60]
lagged_correlations = {}

for lag in lags:
    merged_data[f'Vaccination_Lagged_{lag}'] = merged_data['COVID-19 doses (daily, 7-day average)'].shift(lag)
    temp_data = merged_data.dropna(subset=[f'Vaccination_Lagged_{lag}'])
    lagged_correlation = temp_data[f'Vaccination_Lagged_{lag}'].corr(temp_data['New_cases'])
    lagged_correlations[lag] = lagged_correlation

st.write("Correlations with lagged vaccination rates:")
for lag, corr in lagged_correlations.items():
    st.write(f"Correlation with a {lag}-day lag: {corr:.3f}")
st.image("img/covid_news.png")
#########################

#########################
st.write("Y3: O creștere a numărului total de doze administrate este asociată cu o rată mai scăzută de creștere a cazurilor și deceselor cumulative în Republica Moldova.")
moldova_global_data = global_data[global_data['Country'] == 'Republic of Moldova']
moldova_vaccination_data = vaccination_data[vaccination_data['Entity'] == 'Moldova']

moldova_global_data['Date_reported'] = pd.to_datetime(moldova_global_data['Date_reported'])
moldova_vaccination_data['Day'] = pd.to_datetime(moldova_vaccination_data['Day'])

moldova_merged_data = pd.merge(
    moldova_global_data,
    moldova_vaccination_data,
    left_on='Date_reported',
    right_on='Day',
    how='inner'
)

moldova_merged_data['Cumulative_doses'] = moldova_merged_data['COVID-19 doses (daily, 7-day average)'].cumsum()
moldova_merged_data['Case_growth_rate'] = moldova_merged_data['Cumulative_cases'].pct_change().fillna(0)
moldova_merged_data['Death_growth_rate'] = moldova_merged_data['Cumulative_deaths'].pct_change().fillna(0)

fig, ax1 = plt.subplots(figsize=(14, 7))

ax1.plot(
    moldova_merged_data['Date_reported'],
    moldova_merged_data['Cumulative_doses'],
    label="Cumulative Vaccination Doses",
    color='blue'
)
ax1.set_xlabel("Date")
ax1.set_ylabel("Cumulative Doses", color='blue')
ax1.tick_params(axis='y', labelcolor='blue')
ax1.legend(loc="upper left")

ax2 = ax1.twinx()
ax2.plot(
    moldova_merged_data['Date_reported'],
    moldova_merged_data['Case_growth_rate'],
    label="Case Growth Rate",
    color='orange',
    linestyle='--'
)
ax2.plot(
    moldova_merged_data['Date_reported'],
    moldova_merged_data['Death_growth_rate'],
    label="Death Growth Rate",
    color='red',
    linestyle='--'
)
ax2.set_ylabel("Growth Rate", color='red')
ax2.tick_params(axis='y', labelcolor='red')
ax2.legend(loc="upper right")

plt.title("Relația dintre numărul total de doze administrate și rata de creștere a cazurilor și deceselor cumulative în Moldova")
plt.grid()
plt.show()

st.pyplot(plt)
#########################

#########################
st.write("Y4: Mortalitatea cauzată de COVID-19 scade proporțional cu creșterea ratei de vaccinare în Moldova.")

moldova_merged_data['Mortality_rate'] = (
    moldova_merged_data['Cumulative_deaths'] / moldova_merged_data['Cumulative_cases']
).fillna(0)
moldova_merged_data['Smoothed_mortality_rate'] = moldova_merged_data['Mortality_rate'].rolling(window=7).mean()

fig, ax1 = plt.subplots(figsize=(14, 7))

ax1.plot(
    moldova_merged_data['Date_reported'],
    moldova_merged_data['Cumulative_doses'],
    label="Cumulative Vaccination Doses",
    color='blue'
)
ax1.set_xlabel("Date")
ax1.set_ylabel("Cumulative Doses", color='blue')
ax1.tick_params(axis='y', labelcolor='blue')
ax1.legend(loc="upper left")

ax2 = ax1.twinx()
ax2.plot(
    moldova_merged_data['Date_reported'],
    moldova_merged_data['Smoothed_mortality_rate'],
    label="Smoothed Mortality Rate (7-day average)",
    color='red'
)
ax2.set_ylabel("Mortality Rate", color='red')
ax2.tick_params(axis='y', labelcolor='red')
ax2.legend(loc="upper right")

plt.title("Relația dintre rata de vaccinare și mortalitatea cauzată de COVID-19 în Moldova")
plt.grid()
plt.show()

st.pyplot(plt)

mortality_correlation = moldova_merged_data['Cumulative_doses'].corr(moldova_merged_data['Mortality_rate'])
st.write(mortality_correlation)
#########################

#########################
st.write("Y5: Moldova are rate de vaccinare mai scăzute decât media regiunii, dar impactul vaccinării este similar în ceea ce privește reducerea cazurilor și a mortalității.")

european_countries = [
    'Moldova', 'Romania', 'Ukraine', 'Bulgaria', 'Hungary', 'Serbia',
    'Germany', 'France', 'Italy', 'Spain', 'Poland', 'Netherlands',
    'Sweden', 'Norway', 'Greece', 'Portugal', 'Belgium', 'Austria',
    'Czechia', 'Denmark', 'Finland', 'Ireland', 'Slovakia', 'Slovenia',
    'Croatia', 'Estonia', 'Latvia', 'Lithuania', 'Luxembourg', 'Iceland'
]

european_populations = {
    'Moldova': 2657637,
    'Romania': 19237691,
    'Ukraine': 44134693,
    'Bulgaria': 6927288,
    'Hungary': 9749763,
    'Serbia': 6982084,
    'Germany': 83129285,
    'France': 65273511,
    'Italy': 60367477,
    'Spain': 47351567,
    'Poland': 38386000,
    'Netherlands': 17441139,
    'Sweden': 10353442,
    'Norway': 5421241,
    'Greece': 10345697,
    'Portugal': 10196709,
    'Belgium': 11589623,
    'Austria': 8917205,
    'Czechia': 10708981,
    'Denmark': 5818553,
    'Finland': 5540720,
    'Ireland': 4937786,
    'Slovakia': 5456362,
    'Slovenia': 2078654,
    'Croatia': 4105267,
    'Estonia': 1326535,
    'Latvia': 1886198,
    'Lithuania': 2722289,
    'Luxembourg': 634814,
    'Iceland': 366425
}

european_vaccination_data = vaccination_data[vaccination_data['Entity'].isin(european_countries)]

european_vaccination_summary = (
    european_vaccination_data.groupby('Entity')['COVID-19 doses (daily, 7-day average)']
    .sum()
    .reset_index()
    .rename(columns={'COVID-19 doses (daily, 7-day average)': 'Total_doses'})
)
european_vaccination_summary['Population'] = european_vaccination_summary['Entity'].map(european_populations)
european_vaccination_summary['Vaccination_rate_per_capita'] = (
    european_vaccination_summary['Total_doses'] / european_vaccination_summary['Population']
)

plt.figure(figsize=(16, 8))
plt.bar(
    european_vaccination_summary['Entity'],
    european_vaccination_summary['Vaccination_rate_per_capita'],
    color='skyblue',
    edgecolor='black'
)
plt.title("Compararea ratei de vaccinare per capita între țările europene")
plt.xlabel("Țări")
plt.ylabel("Rata de vaccinare per capita")
plt.xticks(rotation=90)
plt.grid(axis='y')

plt.tight_layout()
plt.show()

st.pyplot(plt)

correlation_results = []

for country in vaccination_data['Entity'].unique():
    country_vaccination = vaccination_data[vaccination_data['Entity'] == country]
    country_global = global_data[global_data['Country'] == country]

    merged_country_data = pd.merge(
        country_vaccination,
        country_global,
        left_on='Day',
        right_on='Date_reported',
        how='inner'
    )

    if len(merged_country_data) > 1:
        cases_corr = merged_country_data[
            ['COVID-19 doses (daily, 7-day average)', 'New_cases']
        ].corr().iloc[0, 1]

        deaths_corr = merged_country_data[
            ['COVID-19 doses (daily, 7-day average)', 'New_deaths']
        ].corr().iloc[0, 1]

        correlation_results.append({
            'Country': country,
            'Cases Correlation': cases_corr,
            'Deaths Correlation': deaths_corr
        })

correlation_df = pd.DataFrame(correlation_results)

st.write(""" 
	Cases Correlation:
	    -Mean: 0.113 (slightly positive on average, but variable across countries)
	    -Range: -0.347 (weak negative) to 0.711 (moderate positive)

	Deaths Correlation:
	    -Mean: 0.172 (slightly positive on average)
	    -Range: -0.448 (weak negative) to 0.805 (moderate positive)
""")
st.dataframe(correlation_df)
#########################

st.write(""" 
Deși Moldova are o rată mai mică de vaccinare, impactul vaccinării asupra reducerii mortalității este similar cu cel observat în alte țări europene. Cu toate acestea, eficiența vaccinării poate fi afectată de infrastructura medicală, disponibilitatea dozelor și alte măsuri de sănătate publică.
""")

st.title("Cum a fost elaborat totul ?")

st.subheader("Streamlit")
st.image("img/streamlit.png")
st.subheader("Github Codespace")
st.image("img/codespace.png")
st.subheader("MongoDB")
st.image("img/collections.png")
st.image("img/documents.png")
