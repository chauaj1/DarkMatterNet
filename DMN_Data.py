import numpy as np
import pandas as pd
import tensorflow as tf


# [Reminder] List of column names assigned when the Illustris dataset is loaded
ILLUSTRIS_COLUMN_NAMES = ['Pre_Drop_Index',
                            'SubhaloBHMass',
                            'SubhaloBHMdot',
                            'SubhaloGasMetallicity',
                            'SubhaloGasMetallicityHalfRad',
                            'SubhaloGasMetallicityMaxRad',
                            'SubhaloGasMetallicitySfr',
                            'SubhaloGasMetallicitySfrWeighted',
                            'SubhaloGrNr',
                            'SubhaloHalfmassRad',
                            'SubhaloIDMostbound',
                            'SubhaloLen',
                            'SubhaloMass',
                            'SubhaloMassInHalfRad',
                            'SubhaloMassInMaxRad',
                            'SubhaloMassInRad',
                            'SubhaloParent',
                            'SubhaloSFR',
                            'SubhaloSFRinHalfRad',
                            'SubhaloSFRinMaxRad',
                            'SubhaloSFRinRad',
                            'SubhaloStarMetallicity',
                            'SubhaloStarMetallicityHalfRad',
                            'SubhaloStarMetallicityMaxRad',
                            'SubhaloStellarPhotometricsMassInRad',
                            'SubhaloStellarPhotometricsRad',
                            'SubhaloVelDisp',
                            'SubhaloVmax',
                            'SubhaloVmaxRad',
                            'SubhaloWindMass',
                            'SubhaloSublinkID',
                            'SubhaloHalfmassRadType0',
                            'SubhaloHalfmassRadType1',
                            'SubhaloHalfmassRadType2',
                            'SubhaloHalfmassRadType3',
                            'SubhaloHalfmassRadType4',
                            'SubhaloHalfmassRadType5',
                            'SubhaloMassInHalfRadType0',
                            'SubhaloMassInHalfRadType1',
                            'SubhaloMassInHalfRadType2',
                            'SubhaloMassInHalfRadType3',
                            'SubhaloMassInHalfRadType4',
                            'SubhaloMassInHalfRadType5',
                            'SubhaloMassInMaxRadType0',
                            'SubhaloMassInMaxRadType1',
                            'SubhaloMassInMaxRadType2',
                            'SubhaloMassInMaxRadType3',
                            'SubhaloMassInMaxRadType4',
                            'SubhaloMassInMaxRadType5',
                            'SubhaloMassInRadType0',
                            'SubhaloMassInRadType1',
                            'SubhaloMassInRadType2',
                            'SubhaloMassInRadType3',
                            'SubhaloMassInRadType4',
                            'SubhaloMassInRadType5',
                            'SubhaloMassType0',
                            'SubhaloMassType1',
                            'SubhaloMassType2',
                            'SubhaloMassType3',
                            'SubhaloMassType4',
                            'SubhaloMassType5',
                            'SubhaloStellarPhotometricsU',
                            'SubhaloStellarPhotometricsB',
                            'SubhaloStellarPhotometricsV',
                            'SubhaloStellarPhotometricsK',
                            'SubhaloStellarPhotometricsg',
                            'SubhaloStellarPhotometricsr',
                            'SubhaloStellarPhotometricsi',
                            'SubhaloStellarPhotometricsz',
                            'SubhaloID',
                            'B300',
                            'B1000',
                            'TotalSFRMass']

# [Reminder] List of column names assigned when the NYU dataset is loaded
# NOTE: NYU column names must match Illustris column names
NYU_COLUMN_NAMES = ['Pre_Drop_Index',
                    'SubhaloMassInRadType4',
                    'SubhaloGasMetallicity',
                    'B300',
                    'B1000']



def raw_dataframe():
    """Function which loads Illustris and NYU datasets"""

    # Load data from Illustris_V3.csv and reassign column names
    #   NOTE: Illustris_V3.csv pre-filtering: halos with 0 stellar mass (SubhaloMassInRadType4) were dropped
    #   NOTE: Illustris_V3.csv pre-filtering was done to reduce the size of CSV
    iDF = pd.read_csv("Illustris_V3.csv",
                        header=0,
                        names=ILLUSTRIS_COLUMN_NAMES,
                        dtype=np.float64)

    # Load data from NYU.csv and reassign column names
    #   NOTE: NYU.csv pre-filtering: halos with 0 stellar mass were dropped
    nDF = pd.read_csv("NYU.csv",
                        header=0,
                        names=NYU_COLUMN_NAMES,
                        dtype=np.float64)

    return iDF, nDF



def load_data(label_name='SubhaloMassInRad', train_fraction=0.8, seed=None):
    """Function which loads Illustris, NYU datasets; returns filtered Train & Test Set from Illustris, Predict Set from NYU"""

    # Use raw_dataframe() to load Illustris and NYU datasets
    iData, nData = raw_dataframe()

    # NYU: Convert NYU stellar mass to units of 10^10 Mstar, like in Illustris
    nData.SubhaloMassInRadType4 /= (10**10)

    # Illustris: Correct Particle Type 4 to only include stellar mass and no wind mass
    iData.SubhaloMassInRadType4 -= iData.SubhaloWindMass

    # Illustris: Make sure all halos havve positive stellar mass
    iData_stell_cut = iData.drop(iData[iData.SubhaloMassInRadType4 < 0].index)

    # Illustris: remove halos with halo mass < 10^9 Mstar
    iData_halo_cut = iData_stell_cut.drop(iData_stell_cut[iData_stell_cut.SubhaloMassInRad < 0.1].index)

    # NYU: remove halos with stellar mass < 10^4 Mstar
    #   NOTE: The Illustris dataset has no halos with stellar mass < 10^4; prediction data must be within trainin data
    nData_stell_cut = nData.drop(nData[nData.SubhaloMassInRadType4 < 0.0000001].index)

    # NYU: remove halos with stellar mass > 1.5 * 10^12 make_one_shot_iterator
    #   NOTE: The Illustris dataset has no halos above 1.5*10^12; prediction data must be within training data
    nData_stell_top_cut = nData_stell_cut.drop(nData_stell_cut[nData_stell_cut.SubhaloMassInRadType4 >= 150].index)

    # Illustris: Split dataframe randomly into a Train Set (80% of data) and a Test Set (20% of data)
    np.random.seed(seed)
    train_features = iData_halo_cut.sample(frac=train_fraction, random_state=seed)
    test_features = iData_halo_cut.drop(train_features.index)

    # Illustris: Store Labels (halo masses) from Train & Test Sets in new seperate dataframes
    train_label = train_features.pop(label_name)
    test_label = test_features.pop(label_name)

    # NYU: Clean name for NYU dataframe
    NYU_features = nData_stell_top_cut

    # Return a pair of dataframes (features only, label only) for Train & Test Sets, single for Predict Set features
    return (train_features, train_label), (test_features, test_label), NYU_features



def make_dataset(features, label):
    """Function which takes in {features} and {label} dataframes and returns a TF Dataset"""

    # Make a dictionary with column names as keys and all following rows as values
    features = dict(features)

    # If there are labels (i.e. Train and Test Sets), include them in the TF Dataset
    # If there are no labels (i.e. NYU Predict Set), do not include them in the TF Dataset
    if label is None:
        inputs = features
    else:
        inputs = (features, label)

    # Create a TF Dataset, where each element contains {features} and {the label} for a single halo
    return tf.data.Dataset.from_tensor_slices(inputs)
