from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from cars.models import MLModel, PredictionHistory, Car
from django.db.models import Q
import numpy as np

FEATURE_COLUMNS = [
    'manufacturer', 'car_class', 'energy_type',
    'motor_power', 'max_horsepower', 'max_speed', 'fuel_tank_volume',
    'curb_weight', 'wheelbase', 'max_torque', 'nedc_fuel_consumption',
    'gear_count', 'width', 'displacement', 'acceleration_time',
    'electric_range', 'front_track', 'seat_count'
]

CATEGORICAL_COLUMNS = ['manufacturer', 'car_class', 'energy_type']

@api_view(['GET'])
@permission_classes([AllowAny])
def get_models(request):
    models = MLModel.objects.all().order_by('-created_at')
    data = []
    for m in models:
        data.append({
            'id': m.id,
            'name': m.name,
            'version': m.version,
            'model_type': m.model_type,
            'is_active': m.is_active,
            'metrics': m.metrics,
            'feature_defaults': m.feature_defaults,
            'description': m.description,
            'created_at': m.created_at.strftime('%Y-%m-%d %H:%M:%S')
        })
    return Response(data)

@api_view(['POST'])
@permission_classes([AllowAny])
def set_active_model(request, model_id):
    try:
        model = MLModel.objects.get(id=model_id)
        MLModel.objects.update(is_active=False)
        model.is_active = True
        model.save()
        return Response({'message': f'模型 {model.name} v{model.version} 已激活'})
    except MLModel.DoesNotExist:
        return Response({'error': '模型不存在'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def delete_model(request, model_id):
    try:
        model = MLModel.objects.get(id=model_id)
        if model.is_active:
            return Response({'error': '无法删除当前激活的模型'}, status=status.HTTP_400_BAD_REQUEST)
        model.delete()
        return Response({'message': '模型已删除'})
    except MLModel.DoesNotExist:
        return Response({'error': '模型不存在'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_feature_options(request):
    manufacturers = list(Car.objects.values_list('manufacturer', flat=True).distinct().order_by('manufacturer'))
    car_classes = list(Car.objects.values_list('car_class', flat=True).distinct().order_by('car_class'))
    energy_types = list(Car.objects.values_list('energy_type', flat=True).distinct().order_by('energy_type'))
    
    return Response({
        'manufacturers': manufacturers,
        'car_classes': car_classes,
        'energy_types': energy_types,
        'feature_columns': FEATURE_COLUMNS,
        'energy_type_config': {
            '纯电动': {
                'hidden_fields': ['fuel_tank_volume', 'nedc_fuel_consumption', 'displacement'],
                'required_fields': ['motor_power', 'electric_range']
            },
            '氢燃料电池': {
                'hidden_fields': ['fuel_tank_volume', 'nedc_fuel_consumption', 'displacement'],
                'required_fields': ['motor_power', 'electric_range']
            },
            '插电式混合动力': {
                'hidden_fields': [],
                'required_fields': ['motor_power', 'electric_range', 'fuel_tank_volume', 'nedc_fuel_consumption']
            },
            '增程式': {
                'hidden_fields': [],
                'required_fields': ['motor_power', 'electric_range', 'fuel_tank_volume', 'nedc_fuel_consumption']
            }
        },
        'feature_info': {
            'manufacturer': {'type': 'categorical', 'label': '厂商'},
            'car_class': {'type': 'categorical', 'label': '级别'},
            'energy_type': {'type': 'categorical', 'label': '能源类型'},
            'motor_power': {'type': 'numeric', 'label': '电动机总功率(kW)', 'unit': 'kW'},
            'max_horsepower': {'type': 'numeric', 'label': '最大马力(Ps)', 'unit': 'Ps'},
            'max_speed': {'type': 'numeric', 'label': '最高车速(km/h)', 'unit': 'km/h'},
            'fuel_tank_volume': {'type': 'numeric', 'label': '油箱容积(L)', 'unit': 'L'},
            'curb_weight': {'type': 'numeric', 'label': '整备质量(kg)', 'unit': 'kg'},
            'wheelbase': {'type': 'numeric', 'label': '轴距(mm)', 'unit': 'mm'},
            'max_torque': {'type': 'numeric', 'label': '最大扭矩(N·m)', 'unit': 'N·m'},
            'nedc_fuel_consumption': {'type': 'numeric', 'label': 'NEDC综合油耗(L/100km)', 'unit': 'L/100km'},
            'gear_count': {'type': 'numeric', 'label': '挡位数', 'unit': ''},
            'width': {'type': 'numeric', 'label': '宽(mm)', 'unit': 'mm'},
            'displacement': {'type': 'numeric', 'label': '排量(mL)', 'unit': 'mL'},
            'acceleration_time': {'type': 'numeric', 'label': '官方百公里加速时间(s)', 'unit': 's'},
            'electric_range': {'type': 'numeric', 'label': '纯电续航里程(km)', 'unit': 'km'},
            'front_track': {'type': 'numeric', 'label': '前轮距(mm)', 'unit': 'mm'},
            'seat_count': {'type': 'numeric', 'label': '座位数(个)', 'unit': '个'},
        }
    })

@api_view(['POST'])
@permission_classes([AllowAny])
def predict_price(request):
    try:
        input_features = request.data.get('features', {})
        model_id = request.data.get('model_id')
        
        if model_id:
            ml_model = MLModel.objects.get(id=model_id)
        else:
            ml_model = MLModel.objects.filter(is_active=True).first()
        
        if not ml_model:
            return Response({'error': '没有可用的模型'}, status=status.HTTP_400_BAD_REQUEST)
        
        model = ml_model.get_model()
        label_encoders = ml_model.get_label_encoders()
        feature_names = ml_model.feature_names
        feature_defaults = ml_model.feature_defaults or {}
        
        energy_type = input_features.get('energy_type', '')
        if energy_type in ['纯电动', '氢燃料电池']:
            input_features['fuel_tank_volume'] = 0
            input_features['nedc_fuel_consumption'] = 0
            input_features['displacement'] = 0
        
        feature_values = []
        for col in feature_names:
            value = input_features.get(col)
            
            if col in CATEGORICAL_COLUMNS and col in label_encoders:
                le = label_encoders[col]
                if value and str(value) in le.classes_:
                    value = le.transform([str(value)])[0]
                else:
                    value = le.transform(['Unknown'])[0] if 'Unknown' in le.classes_ else 0
            else:
                if value is None or value == '':
                    value = feature_defaults.get(col, 0)
                try:
                    value = float(value)
                except (TypeError, ValueError):
                    value = feature_defaults.get(col, 0)
            
            feature_values.append(float(value))
        
        X = np.array([feature_values])
        predicted_price = model.predict(X)[0]
        predicted_price = max(0, predicted_price)
        
        user = request.user if request.user.is_authenticated else None
        PredictionHistory.objects.create(
            input_features=input_features,
            predicted_price=round(predicted_price, 2),
            model_used=ml_model,
            user=user
        )
        
        return Response({
            'predicted_price': round(predicted_price, 2),
            'model_name': ml_model.name,
            'model_version': ml_model.version,
            'model_metrics': ml_model.metrics
        })
        
    except MLModel.DoesNotExist:
        return Response({'error': '模型不存在'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_prediction_history(request):
    history = PredictionHistory.objects.filter(user=request.user).order_by('-created_at')[:20]
    data = []
    for h in history:
        input_features = h.input_features or {}
        data.append({
            'id': h.id,
            'manufacturer': input_features.get('manufacturer', ''),
            'car_class': input_features.get('car_class', ''),
            'energy_type': input_features.get('energy_type', ''),
            'motor_power': input_features.get('motor_power'),
            'electric_range': input_features.get('electric_range'),
            'acceleration_time': input_features.get('acceleration_time'),
            'predicted_price': h.predicted_price,
            'model_name': h.model_used.name if h.model_used else 'Unknown',
            'created_at': h.created_at.strftime('%Y-%m-%d %H:%M:%S')
        })
    return Response(data)

@api_view(['POST'])
@permission_classes([AllowAny])
def get_similar_cars(request):
    features = request.data.get('features', {})
    predicted_price = request.data.get('predicted_price')
    
    manufacturer = features.get('manufacturer')
    car_class = features.get('car_class')
    energy_type = features.get('energy_type')
    
    qs = Car.objects.all()
    if manufacturer:
        qs = qs.filter(manufacturer=manufacturer)
    if car_class:
        qs = qs.filter(car_class=car_class)
    if energy_type:
        qs = qs.filter(energy_type=energy_type)
    
    if predicted_price is not None:
        try:
            p = float(predicted_price)
            qs = qs.filter(price__gte=max(0, p - 10), price__lte=p + 10)
        except (TypeError, ValueError):
            pass
    
    qs = qs.order_by('price')[:10]
    data = list(qs.values(
        'id', 'model_name', 'manufacturer', 'car_class', 'energy_type',
        'motor_power', 'max_horsepower', 'max_speed', 'electric_range',
        'acceleration_time', 'price'
    ))
    return Response({'similar_cars': data})
