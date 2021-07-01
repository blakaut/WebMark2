from rest_framework import status
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from qleader.models import QBatch
from qleader.helpers import create_qresults, create_qbatch
import json


@api_view(['GET', 'POST'])
def result_list(request):

    if request.method == 'GET':
        return Response()
    elif request.method == 'POST':
        data_dict = json.loads(request.data)
        try:
            batch = create_qbatch(data_dict)
            batch.save()
            qresults = create_qresults(data_dict, batch)
            lowest_energy = float("inf")
            for qresult in qresults:
                if qresult.energy < lowest_energy:
                    lowest_energy = qresult.energy
                qresult.save()
            batch.min_energy = lowest_energy
            batch.save()
            return Response('Success', status=status.HTTP_201_CREATED)
        except Exception as e:
            try:
                batch.delete()
            except:
                pass
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@renderer_classes([TemplateHTMLRenderer])
def home(request):

    if request.method == 'GET':
        results = QBatch.objects.all().order_by('created')
        # Here we can filter the list before displaying
        return Response({'results': results.values(),
                        'path_prefix': request.headers.get('PathPrefix', '')},
                        template_name='home.html')


@api_view(['GET'])
@renderer_classes([TemplateHTMLRenderer])
def detail(request, batch_id):

    if request.method == 'GET':
        qbatch = QBatch.objects.filter(id=batch_id)[0]
        results = qbatch.results.all()

        distances = [result.distance for result in results]
        energies = [result.energy for result in results]

        name = ' '.join([qbatch.basis_set, qbatch.transformation])

        return Response({'batch': qbatch,
                         'results': results,
                         'name': name,
                         'energies': energies,
                         'distances': distances,
                         'path_prefix': request.headers.get('PathPrefix', '')},
                        template_name='detail.html')

@api_view(['GET'])
@renderer_classes([TemplateHTMLRenderer])
def leaderboard(request):

    result_list = QBatch.objects.order_by("min_energy")[:10]

    return Response({'results': result_list}, template_name='leaderboard.html')