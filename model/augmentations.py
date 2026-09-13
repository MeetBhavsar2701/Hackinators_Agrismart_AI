import albumentations as A

def get_train_transforms(image_size=224):
    """
    Returns the augmentation pipeline for training, 
    designed to simulate field conditions (uneven lighting, occlusion, etc).
    """
    return A.Compose([
        A.RandomResizedCrop(size=(image_size, image_size), scale=(0.8, 1.0)),
        A.HorizontalFlip(p=0.5),
        A.Affine(scale=(0.95, 1.05), translate_percent=(-0.05, 0.05), rotate=(-15, 15), p=0.5),
        A.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.1, p=0.5),
        A.CoarseDropout(
            num_holes_range=(1, 1),
            hole_height_range=(int(image_size * 0.1), int(image_size * 0.2)),
            hole_width_range=(int(image_size * 0.1), int(image_size * 0.2)),
            p=0.5
        )
    ])

def get_val_transforms(image_size=224):
    """
    Returns the augmentation pipeline for validation and testing.
    """
    return A.Compose([
        A.Resize(height=image_size, width=image_size),
    ])
