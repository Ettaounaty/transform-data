import os
import streamlit as st
from datetime import date, datetime, timedelta
import pandas as pd
import io  # Importer le module io


st.set_page_config(layout="wide", page_title='Banyan Tree')  # Définit la page en mode wide





st.image('logo1.png', width=155)

# Définition des styles CSS pour la barre de navigation
css = f"""
    <style>
        .navbar {{
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 1rem;
            background-color: #333; /* Couleur de fond */
            color: white; /* Couleur du texte */
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1); /* Ombre */
            font-size: 24px;
        }}
        .date {{
            font-size: 20px;
        }}
    </style>
"""

# Affichage de la barre de navigation avec la date
st.markdown(css, unsafe_allow_html=True)
st.markdown(
    f"""
    <div class="navbar">
        <p class="date">{date.today()}</p>
    </div>
    """,
    unsafe_allow_html=True
)



# Titre de l'application
st.title('Importation et Manipulation de Fichiers Texte')



# Section pour importer le fichier
st.header('Importer votre fichier texte')
uploaded_file = st.file_uploader("Choisissez un fichier texte", type=['txt'])

if uploaded_file is not None:
    # Lecture du fichier texte
    data = pd.read_csv(uploaded_file, delimiter=';', header=None, index_col=None)
    st.write("Aperçu du fichier importé :")
    st.write(data)

    # Demander à l'utilisateur s'il souhaite appliquer des transformations
    apply_transformations = st.radio("Voulez-vous appliquer des transformations sur ces données ?", ('Oui', 'Non'), index=(1))

    if apply_transformations == 'Oui':
        # Manipulations avec le code Python que vous avez déjà
        #supprimer les trois premiers colonnes
        data.drop(columns=[0,1,2,8,11,12], inplace=True)
        # Renommer les colonnes restantes
        nouveaux_noms = {3: 'Compte US', 4: 'Analytic', 5: 'Departement', 6: 'Compte Marocaine', 7: 'Description', 9: 'signe', 10: 'montant'}
        data = data.rename(columns=nouveaux_noms)

        data['Departement'] = data['Departement'].astype(str).str.replace('=', '')
        data['Departement'] = data['Departement'].astype(str).str.replace('"', '')
        data['Analytic'] = data['Analytic'].astype(str).str.replace('=', '')
        data['Analytic'] = data['Analytic'].astype(str).str.replace('"', '')
        data['Description'] = data['Description'].astype(str).str.replace('=', '')
        data['Description'] = data['Description'].astype(str).str.replace('"', '')
        data['Compte US'] = data['Compte US'].astype(str).str.replace('=', '')
        data['Compte US'] = data['Compte US'].astype(str).str.replace('"', '')
        data['Compte Marocaine'] = data['Compte Marocaine'].astype(str).str.replace('=', '')
        data['Compte Marocaine'] = data['Compte Marocaine'].astype(str).str.replace('"', '')
        data['montant'] = data['montant'].astype(str).str.replace(',', '')
        data['montant'] = data['montant'].astype(str).str.replace('000', '')
        

        
        #Supprimer les lignes où la valeur dans la colonne “montant" égale à 0
        data=data[(data['montant']!='')]
        # Supprimer les lignes où 'compte marocaine' commence par '6' et 'analytic' est vide
        data = data[~((data['Compte Marocaine'].astype(str).str.startswith('6')) & (data['Analytic'].isnull()))]
        #remplacer la valeur de dpartement par "551" ou compte marocaine=71972001
        data.loc[data['Compte Marocaine']== 71972001, "Departement"]= "551"
        #remplacer la valeur de dpartement par "531" ou compte marocaine=71973001
        data.loc[data['Compte Marocaine']== 71973001, 'Departement']= '531'
        #supprimer les lignes ou 'compte marocaine' commence par '7' et 'analytic' est vide 
        data=data[~((data['Compte Marocaine'].astype(str).str.startswith('7')) & (data['Analytic'].isnull()))]
        #multiplier montant par "-1" si le signe=C
        data.loc[data['signe']=='C', 'montant']*= -1
        #supprimer les colonnes "signe" et "Analytic"
        data.drop(columns=['signe', 'Analytic'], inplace=True)
        #ajouter colonne devise avec la valeur "MAD"
        data['Devise']='MAD'
        #recuperer colonne departement puis le supprimer puis l'inserer au dernier position
        Departement=data['Departement']
        data.drop(columns=['Departement'], inplace=True)
        data['Departement']=Departement
        #pour la date actuelle
        date_actuelle = datetime.now()
        #ajouter colonne "date" contenant la date de deernier jour de mos precedent
        data['Date'] =(date_actuelle.replace(day=1) - timedelta(days=1)).date()
        # Convertir la colonne 'Date' en type datetime
        data['Date'] = pd.to_datetime(data['Date'])
        # Extraire l'année et le mois pour former la colonne 'Période'
        data['Période'] = data['Date'].dt.strftime('%Y%m')  
        data['Période'] = data['Période'].str.slice(0, 4) + data['Date'].dt.strftime('%m').str.zfill(3)
        #ajouter la colonne reference en concaténant la chaîne "Paie perm mois" avec l'année et le mois.
        data['Référence'] = 'Paie perm mois ' + data['Date'].dt.strftime('%m-%Y')
        # Limiter à 30 caractères si nécessaire
        data['Référence'] = data['Référence'].str[:30] 

        data['Compte Marocaine'] = data['Compte Marocaine'].astype(str).str.replace(',', '')
        data['Compte US'] = data['Compte US'].astype(str).str.replace(',', '')
        #data['montant'] = data['montant'].astype(str).str.replace(',', '')

        
        st.write("Manipulations appliquées :")
        st.write(data)  # Afficher un aperçu des données après manipulation
        
        # Section d'exportation vers Excel avec choix de l'emplacement
        
        #st.header("Exporter vers Excel")
        #export_location = st.text_input("Entrez le chemin de destination pour l'exportation")

        #if st.button("Exporter vers Excel") and export_location:
            # Vérification de l'existence du dossier de destination
            #if not os.path.exists(export_location):
                #st.error("Le chemin spécifié n'existe pas.")
            #else:
                # Obtention de la date actuelle
                #current_date = datetime.now().strftime("%Y-%m-%d")
                # Concaténation du chemin avec le nom du fichier Excel incluant la date
                #excel_file_name = f"data_{current_date}.xlsx"
                #excel_file_path = os.path.join(export_location, excel_file_name)
                # Exportation vers Excel
                #data.to_excel(excel_file_path, index=False)
                #st.success(f"Exportation réussie vers {excel_file_path}")
         

        # Bouton pour exporter en fichier Excel
        #if st.button("Exporter en fichier Excel"):
         #   file_path = "C:\\Users\\ns\\OneDrive\\Bureau\\output.xlsx"  # Chemin où le fichier Excel sera enregistré
          #  data.to_excel(file_path, index=False)  # Exportation du DataFrame en fichier Excel
            #st.success(f"Le fichier Excel a été créé : {file_path}")


        
        


    



   

    
