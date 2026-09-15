# Sample image

`tomato_early_blight_field.jpg` — one real field-condition leaf photo, included so
that `predict.py` can be run immediately without downloading a dataset.

| | |
|---|---|
| **Source** | [PlantDoc-Dataset](https://github.com/pratikkayal/PlantDoc-Dataset), `test/Tomato Early blight leaf/` |
| **Ground truth** | Tomato — Early blight |
| **Expected model label** | `Tomato___Early_blight` |
| **Citation** | Singh et al., *PlantDoc: A Dataset for Visual Plant Disease Detection*, CODS-COMAD 2020 (arXiv:1911.10317) |

This is a **field-condition** image, i.e. from the domain where our model scores
0.0690 macro-F1. A wrong prediction here is consistent with the limitation
documented in [`../report/model_report.md`](../report/model_report.md) and is not
a bug in the inference code.

Run:

```bash
python model/predict.py --image samples/tomato_early_blight_field.jpg
```
