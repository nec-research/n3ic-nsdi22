# N3IC

This repository contains the code for the paper

***"Re-architecting Traffic Analysis with Neural Network Interface Cards" (G. Siracusano et al., USENIX NSDI 2022)***

The structure of the directories is the following:
- `dt_rf_bnn`: Jupyter notebooks comparing Decision Tree (DT), Random Forest (RF) and Binary Neural Network (BNN) models on Security and IoT datasets
- `NNtoP4`: BNN to P4 compiler
- `bnn-exec`: CPU BNN executor baseline
- `n3ic-nfp`: NFP BNN executor

Additional `README.md` files are provided in the sub-directories above.

## Reference
If you use N3IC for your research, please cite the following paper:
```
@inproceedings{siracusano2022n3ic,
  title={Re-architecting Traffic Analysis with Neural Network Interface Cards},
  author={Siracusano, Giuseppe and Galea, Salvator and Sanvito, Davide and Malekzadeh, Mohammad and Antichi, Gianni and Costa, Paolo and Haddadi, Hamed and Bifulco, Roberto},
  booktitle={19th USENIX Symposium on Networked Systems Design and Implementation (NSDI 22)},
  year={2022}
}
```
