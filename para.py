import json

PARAS = {
    "circle_mode":{
        "median_blur_kernal":5,
        "gaussian_blur_kernal":11,
        "gaussian_blur_sigma":8,
        "closing_kernal":7,
        "dist_transform_threshold":0.5,
        "area_sigma":1.4
    },
    "rectangle_mode":{
        "median_blur_kernal":5,
        "gaussian_blur_kernal":11,
        "gaussian_blur_sigma":8,
        "closing_kernal":7,
        "dist_transform_threshold":0.15,
        "area_sigma":2

    }
}

print(PARAS["rectangle_mode"])

with open("para.json",'w') as f:
    json.dump(PARAS,f,indent=4,ensure_ascii=False)