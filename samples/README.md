# Sample images

Drop any of these into the web app, or pass them to `predict.py`.

## Lab images — PlantVillage (use these for the demo)

The model classifies all five correctly.

| File | Ground truth | Model output |
|---|---|---|
| `lab_tomato_early_blight.jpg` | Tomato — Early blight | `Tomato___Early_blight` ✓ |
| `lab_potato_late_blight.jpg` | Potato — Late blight | `Potato___Late_blight` ✓ |
| `lab_grape_black_rot.jpg` | Grape — Black rot | `Grape___Black_rot` ✓ |
| `lab_corn_common_rust.jpg` | Corn — Common rust | `Corn_(maize)___Common_rust_` ✓ |
| `lab_tomato_healthy.jpg` | Tomato — healthy | `Tomato___healthy` ✓ |

Source: [PlantVillage-Dataset](https://github.com/spMohanty/PlantVillage-Dataset)
(Hughes & Salathé, 2015), `raw/color/`.

## Field image — PlantDoc (use this to show the honest limitation)

| File | Ground truth |
|---|---|
| `tomato_early_blight_field.jpg` | Tomato — Early blight |

Source: [PlantDoc-Dataset](https://github.com/pratikkayal/PlantDoc-Dataset)
`test/Tomato Early blight leaf/` — Singh et al., CODS-COMAD 2020 (arXiv:1911.10317).

This is a real-world field photo: cluttered background, natural lighting. The
model is trained on lab images only, so accuracy here is much lower and
confidence is correspondingly lower. That gap is the point of the challenge and
is documented in [`../report/model_report.md`](../report/model_report.md).

## Run from the CLI

```bash
python model/predict.py --image samples/lab_tomato_early_blight.jpg
```

## More images

Every class is available from the two dataset repositories linked above. For the
27 classes this model knows, see
[`../model/weights/label_mapping.json`](../model/weights/label_mapping.json).
