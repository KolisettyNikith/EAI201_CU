Zoo Exam Notebook - Automated implementation for Roll 24UG00317, Seat 13

Prefix: Beta

Class: DataExplorer_24UG00317

This script implements the three required methods:

- Beta_load_and_integrate()

- Beta_eda_and_cleaning()

- Beta_train_and_evaluate()

It follows the personalized rules:

- Name normalization: keep original case, deduplicate case-insensitively

- Missing value strategy: Categorical -> "unknown", Numerical -> median

- Feature engineering (Row B): habitat_risk_score, trophic_level, predator_score, ecosystem_type

- Visualization set (Column 1): 4 plots as required

- Train/Test split: 80/20, random_state=789

- RF config (Config C): n_estimators=200, max_depth=10, random_state=789

- Comparison model: SVM

import os import json import re from collections import Counter

import numpy as np import pandas as pd import matplotlib.pyplot as plt import seaborn as sns

from sklearn.model_selection import train_test_split from sklearn.ensemble import RandomForestClassifier from sklearn.svm import SVC from sklearn.metrics import classification_report, confusion_matrix, accuracy_score from sklearn.preprocessing import LabelEncoder

plt.rcParams['figure.figsize'] = (10, 6)

class DataExplorer_24UG00317: def init(self, data_dir='data'): self.data_dir = data_dir self.zoo_path = os.path.join(self.data_dir, 'zoo.csv') self.class_path = os.path.join(self.data_dir, 'class.csv') self.aux_path = os.path.join(self.data_dir, 'auxiliary_metadata.json')

# placeholders
    self.zoo = None
    self.cls = None
    self.aux = None
    self.merged = None
    self.engineered_feature_names = []

    # personalized params
    self.prefix = 'Beta'
    self.name_norm_rule = 'keep_original_case_dedup_case_insensitive'
    self.missing_strategy = {'categorical': 'unknown', 'numerical': 'median'}
    self.train_pct = 0.8
    self.test_pct = 0.2
    self.random_state = 789

    # RF config (Config C)
    self.rf_params = {'n_estimators': 200, 'max_depth': 10, 'random_state': self.random_state}

# ------------------ Helpers ------------------
def _safe_read_csv(self, path):
    # try reading with utf-8 then fallback to latin1
    try:
        return pd.read_csv(path)
    except Exception:
        return pd.read_csv(path, encoding='latin1')

def _load_json_repair(self, path):
    """
    Attempt to robustly load a possibly corrupted JSON file.
    Strategy:
    - Try json.load
    - If fails, do text repairs: remove trailing commas, replace single quotes with double, fix unquoted keys
    - Return dict
    """
    if not os.path.exists(path):
        print(f"Auxiliary JSON not found at {path}")
        return {}

    with open(path, 'r', encoding='utf-8', errors='replace') as f:
        text = f.read()

    # quick try
    try:
        return json.loads(text)
    except Exception:
        pass

    # Repairs
    repaired = text
    # remove JavaScript-style comments
    repaired = re.sub(r'\/\*.*?\*\/', '', repaired, flags=re.DOTALL)
    repaired = re.sub(r'//.*?\n', '\n', repaired)
    # remove trailing commas before } or ]
    repaired = re.sub(r',\s*([}\]])', r'\1', repaired)
    # replace single quotes with double quotes (naive)
    repaired = repaired.replace("\'", '"')

    # attempt to add quotes around unquoted keys: {key: -> "key":
    repaired = re.sub(r'(?P<prefix>[\{,]\s*)(?P<key>[A-Za-z0-9_\-]+)\s*:', r"\g<prefix>\"\g<key>\":", repaired)

    try:
        return json.loads(repaired)
    except Exception as e:
        print('Failed to auto-repair JSON fully:', e)
        # as a last resort, try to extract simple key-value pairs
        kv = {}
        for m in re.finditer(r'"?(?P<k>[A-Za-z0-9_\- ]+)"?\s*:\s*"(?P<v>[^"]+)"', repaired):
            kv[m.group('k').strip()] = m.group('v')
        return kv

# ------------------ Task 1 ------------------
def Beta_load_and_integrate(self):
    """Load zoo.csv, class.csv, auxiliary_metadata.json and merge into a single DataFrame."""
    print('Loading zoo and class CSVs...')
    self.zoo = self._safe_read_csv(self.zoo_path)
    self.cls = self._safe_read_csv(self.class_path)

    print('Attempting to load auxiliary metadata (with repair)...')
    self.aux = self._load_json_repair(self.aux_path)

    # Standardize column names in aux if dict of dicts
    if isinstance(self.aux, dict):
        # If auxiliary metadata maps animal -> metadata, convert to DataFrame
        try:
            # If each value is a dict, create rows
            rows = []
            for k, v in self.aux.items():
                if isinstance(v, dict):
                    row = v.copy()
                    row['animal_name'] = k
                    rows.append(row)
            if rows:
                aux_df = pd.DataFrame(rows)
            else:
                aux_df = pd.DataFrame([self.aux])
            self.aux = aux_df
        except Exception:
            self.aux = pd.DataFrame()
    elif isinstance(self.aux, list):
        self.aux = pd.DataFrame(self.aux)
    else:
        # empty or unrecognized
        self.aux = pd.DataFrame()

    print('Initial shapes:')
    print('zoo:', getattr(self.zoo, 'shape', None))
    print('class:', getattr(self.cls, 'shape', None))
    print('aux:', getattr(self.aux, 'shape', None))

    # Ensure zoo has a name column; guess common names
    possible_name_cols = [c for c in self.zoo.columns if 'name' in c.lower() or 'animal' in c.lower()]
    name_col = possible_name_cols[0] if possible_name_cols else self.zoo.columns[0]
    self.zoo.rename(columns={name_col: 'animal_name'}, inplace=True)

    # class file: ensure it maps class_id to class label
    possible_class_cols = [c for c in self.cls.columns if 'class' in c.lower()]
    if len(possible_class_cols) >= 2:
        # assume first is id, second is textual
        self.cls.columns = ['class_type', 'class_name'] + list(self.cls.columns[2:])
    elif len(possible_class_cols) == 1:
        # keep as-is
        pass

    # Normalize names per rule: keep original case but dedup case-insensitively
    print('Applying name normalization: keep case but deduplicate case-insensitively...')
    self.zoo['animal_name_norm'] = self.zoo['animal_name'].astype(str)
    # Use casefold for case-insensitive deduplication
    self.zoo['animal_name_key'] = self.zoo['animal_name_norm'].str.casefold().str.strip()
    # drop duplicates keeping first occurrence
    before = len(self.zoo)
    self.zoo = self.zoo.drop_duplicates(subset=['animal_name_key']).reset_index(drop=True)
    after = len(self.zoo)
    print(f'Dropped {before - after} duplicate rows based on case-insensitive names')

    # Merge zoo with auxiliary on normalized/casefolded names
    if not self.aux.empty and 'animal_name' in self.aux.columns:
        self.aux['animal_name_key'] = self.aux['animal_name'].astype(str).str.casefold().str.strip()
        merged = pd.merge(self.zoo, self.aux.drop(columns=['animal_name']), on='animal_name_key', how='left', suffixes=('', '_aux'))
    else:
        merged = self.zoo.copy()

    # If class mapping exists, merge class labels
    # try merge on class id column if present
    class_cols = [c for c in self.cls.columns]
    if 'class_name' in self.cls.columns or len(self.cls.columns) >= 2:
        # try to merge by a column named 'type' or 'class_type' if exists
        # fallback: if 'class_type' exists in zoo, merge
        if 'type' in merged.columns and 'class_name' in self.cls.columns:
            merged = pd.merge(merged, self.cls[['type', 'class_name']].drop_duplicates(), on='type', how='left')
        else:
            # try by index (some datasets have the class id in zoo 'class_type' numeric)
            if 'class_type' in merged.columns:
                merged = pd.merge(merged, self.cls, on='class_type', how='left')

    # store merged
    self.merged = merged

    print('Merged dataset shape:', self.merged.shape)
    print('Columns:', list(self.merged.columns))

    # Quick prints required by exam
    print('\nREQUIRED OUTPUT:')
    print('Dataset shape:', self.merged.shape)
    print('Missing values per column:\n', self.merged.isnull().sum())
    print('Duplicate rows count:', self.merged.duplicated().sum())

# ------------------ Task 2 ------------------
def Beta_eda_and_cleaning(self):
    """Perform exploratory data analysis, visualizations, cleaning, feature engineering."""
    if self.merged is None:
        raise ValueError('Run Beta_load_and_integrate first')

    df = self.merged.copy()

    # ---------------- Name normalization already applied. Now fix JSON field inconsistencies if any
    # Standardize common field names if present
    rename_map = {}
    for col in df.columns:
        lc = col.lower()
        if lc in ['conservation_status', 'conservation']:
            rename_map[col] = 'conservation_status'
        if lc in ['habitat', 'habitats']:
            rename_map[col] = 'habitat_type'
        if lc in ['diet', 'diet_type']:
            rename_map[col] = 'diet'
    if rename_map:
        df.rename(columns=rename_map, inplace=True)

    # Fix simple typos in diet values
    if 'diet' in df.columns:
        df['diet'] = df['diet'].astype(str).str.replace('omnivor', 'omnivore', regex=False)
        df['diet'] = df['diet'].astype(str).str.strip().replace({'': np.nan})

    # ---------------- Handle missing values according to strategy
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    cat_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()

    # Numeric -> median
    for c in num_cols:
        median_val = df[c].median()
        df[c] = df[c].fillna(median_val)

    # Categorical -> 'unknown'
    for c in cat_cols:
        df[c] = df[c].fillna(self.missing_strategy['categorical'])

    # ---------------- Feature engineering Row B (seat 11-20)
    # habitat_risk_score: marine=3, freshwater=2, terrestrial=1
    def habitat_risk(h):
        if not isinstance(h, str):
            return 0
        h = h.lower()
        if 'marine' in h:
            return 3
        if 'fresh' in h:
            return 2
        if 'terrestrial' in h or 'land' in h:
            return 1
        return 1

    if 'habitat_type' in df.columns:
        df['habitat_risk_score'] = df['habitat_type'].apply(habitat_risk)
    else:
        # try 'habitat' or default 1
        df['habitat_risk_score'] = df.get('habitat', pd.Series([1]*len(df))).apply(habitat_risk)

    # trophic_level: carnivore=3, omnivore=2, herbivore/other=1
    def trophic(d):
        if not isinstance(d, str):
            return 1
        d = d.lower()
        if 'carn' in d:
            return 3
        if 'omni' in d:
            return 2
        if 'herb' in d:
            return 1
        return 1

    df['trophic_level'] = df.get('diet', pd.Series([np.nan]*len(df))).astype(str).apply(trophic)

    # predator_score: carnivore=3, omnivore=2, herbivore=1
    df['predator_score'] = df['trophic_level']  # same mapping

    # ecosystem_type: terrestrial=0, freshwater=1, marine=2, mixed=3
    def ecosystem(h):
        if not isinstance(h, str):
            return 0
        h = h.lower()
        if 'terrestrial' in h or 'land' in h:
            return 0
        if 'fresh' in h:
            return 1
        if 'marine' in h:
            return 2
        if 'mixed' in h:
            return 3
        return 0

    df['ecosystem_type'] = df.get('habitat_type', df.get('habitat', pd.Series(['']*len(df)))).astype(str).apply(ecosystem)

    # Two custom biological features (simple examples) — explain in comments in notebook
    # metabolism_score: approximate from body mass feature if present
    if 'body_mass' in df.columns:
        df['metabolism_score'] = (df['body_mass'] / (df['body_mass'].max() + 1)).fillna(0)
    else:
        df['metabolism_score'] = 0

    # mobility_score: from number_of_legs or fins (if present)
    if 'legs' in df.columns:
        df['mobility_score'] = df['legs'].apply(lambda x: 1 if x<=2 else (2 if x<=4 else 3))
    else:
        df['mobility_score'] = 1

    # Save engineered features list
    engineered = ['habitat_risk_score', 'trophic_level', 'predator_score', 'ecosystem_type', 'metabolism_score', 'mobility_score']
    self.engineered_feature_names = engineered

    # ---------------- Required visualizations (Column 1 set)
    # Column 1 set: stacked bar chart class distribution by conservation, violin plot feature correlations by class,
    # pairplot top 3 numerical features colored by class, class distribution bar plot with percentages

    # Ensure a class label column exists; attempt to use 'class_name' or 'type' or 'class'
    target_col = None
    for candidate in ['class_name', 'class', 'type', 'class_type']:
        if candidate in df.columns:
            target_col = candidate
            break
    if target_col is None:
        # create synthetic target if missing
        df['class_label'] = df.index % 7  # fallback
        target_col = 'class_label'

    # 1. Stacked bar chart: class distribution by conservation
    if 'conservation_status' in df.columns:
        pivot = pd.crosstab(df[target_col], df['conservation_status'])
        pivot.plot(kind='bar', stacked=True)
        plt.title('Class distribution by conservation status (stacked)')
        plt.xlabel('Class')
        plt.ylabel('Count')
        plt.tight_layout()
        plt.show()

    # 2. Violin plot: feature correlations by class for top numerical features
    num_feats = df.select_dtypes(include=[np.number]).columns.tolist()
    # pick top 4 numeric features excluding engineered names
    top_num = [c for c in num_feats if c not in engineered][:4]
    if top_num:
        # melt for violin plot
        melt = df[[target_col] + top_num].melt(id_vars=target_col, var_name='feature', value_name='value')
        plt.figure(figsize=(12,6))
        sns.violinplot(x='feature', y='value', hue=target_col, data=melt, split=False)
        plt.title('Violin plots of top numeric features by class')
        plt.tight_layout()
        plt.show()

    # 3. Pairplot top 3 numerical features colored by class
    pair_feats = [f for f in top_num][:3]
    if len(pair_feats) >= 1:
        sns.pairplot(df[pair_feats + [target_col]], hue=target_col, diag_kind='kde')
        plt.suptitle('Pairplot of top features by class', y=1.02)
        plt.show()

    # 4. Class distribution bar plot with percentages
    counts = df[target_col].value_counts()
    ax = counts.plot(kind='bar')
    for p in ax.patches:
        ax.annotate(f'{p.get_height()} ({p.get_height()/len(df)*100:.1f}%)', (p.get_x()+p.get_width()/2., p.get_height()), ha='center', va='bottom')
    plt.title('Class distribution with percentages')
    plt.show()

    # ---------------- Statistical analysis
    # Class imbalance ratio
    if target_col in df.columns:
        sizes = df[target_col].value_counts()
        imbalance_ratio = sizes.max() / sizes.min() if sizes.min()>0 else np.inf
        print('Class imbalance ratio (largest/smallest):', imbalance_ratio)

    # Low variance features
    variances = df.select_dtypes(include=[np.number]).var()
    low_var = variances[variances < 0.01].index.tolist()
    print('Low variance features (<0.01):', low_var)

    # Highly correlated pairs
    corr = df.select_dtypes(include=[np.number]).corr().abs()
    high_corr = []
    for i in corr.columns:
        for j in corr.columns:
            if i!=j and corr.loc[i,j] > 0.8:
                high_corr.append((i,j,corr.loc[i,j]))
    print('Highly correlated feature pairs (corr>0.8):', high_corr)

    # Save cleaned merged
    self.merged = df

    # Print required outputs
    print('\nREQUIRED OUTPUT AFTER CLEANING:')
    print('Dataset shape:', df.shape)
    print('Missing values per column:\n', df.isnull().sum())
    print('Engineered features:', self.engineered_feature_names)

# ------------------ Task 3 ------------------
def Beta_train_and_evaluate(self):
    """Prepare data, split, train RF and SVM, evaluate and print reports."""
    if self.merged is None:
        raise ValueError('Run Beta_load_and_integrate and Beta_eda_and_cleaning first')

    df = self.merged.copy()

    # Determine target column
    target_col = None
    for candidate in ['class_name', 'class', 'type', 'class_type', 'class_label']:
        if candidate in df.columns:
            target_col = candidate
            break
    if target_col is None:
        raise ValueError('No target column found')

    # Select features: numeric + engineered
    numeric_feats = df.select_dtypes(include=[np.number]).columns.tolist()
    # remove target if numeric
    if target_col in numeric_feats:
        numeric_feats.remove(target_col)

    X = df[numeric_feats].copy()
    y = df[target_col].copy()

    # encode y if not numeric
    if y.dtype == 'object' or y.dtype.name == 'category':
        le = LabelEncoder()
        y = le.fit_transform(y.astype(str))
    else:
        le = None

    # train/test split per personalized rule
    X_train, X_test, y_train, y_test = train_test_split(X, y, train_size=self.train_pct, random_state=self.random_state, stratify=y if len(np.unique(y))>1 else None)

    print('\nTrain shape:', X_train.shape, 'Test shape:', X_test.shape)

    # Random Forest (primary)
    rf = RandomForestClassifier(**self.rf_params)
    rf.fit(X_train, y_train)
    y_pred_rf = rf.predict(X_test)

    print('\nRandom Forest Performance:')
    print('Accuracy:', accuracy_score(y_test, y_pred_rf))
    print('Classification Report:\n', classification_report(y_test, y_pred_rf))
    print('Confusion Matrix:\n', confusion_matrix(y_test, y_pred_rf))

    # Comparison model: SVM
    svm = SVC(probability=True, random_state=self.random_state)
    try:
        svm.fit(X_train, y_train)
        y_pred_svm = svm.predict(X_test)
        print('\nSVM Performance:')
        print('Accuracy:', accuracy_score(y_test, y_pred_svm))
        print('Classification Report:\n', classification_report(y_test, y_pred_svm))
        print('Confusion Matrix:\n', confusion_matrix(y_test, y_pred_svm))
    except Exception as e:
        print('SVM training failed (maybe scaling needed or insufficient data):', e)

    # Save outputs required by exam
    print('\n--- REQUIRED OUTPUT SUMMARY ---')
    print('Engineered features:', self.engineered_feature_names)
    print('Train/Test shapes:', X_train.shape, X_test.shape)

----------------------- Execute -----------------------

if name == 'main': explorer = DataExplorer_24UG00317(data_dir='data') explorer.Beta_load_and_integrate() explorer.Beta_eda_and_cleaning() explorer.Beta_train_and_evaluate()

To run as a Jupyter notebook, put code blocks into cells and include markdown

For the exam submission: save this as 'Roll_24UG00317_Seat_13_ZooExam.ipynb' (or .py) and also submit auxiliary_metadata.json
