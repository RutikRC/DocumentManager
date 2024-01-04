from rest_framework import status
from rest_framework import generics, permissions
from .models import *
from .serializers import *
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from datetime import datetime
from django.http import Http404


# Create your views here.
class ClientListView(generics.ListCreateAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [permissions.AllowAny]

class ClientDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [permissions.IsAuthenticated]

class JobListView(generics.ListCreateAPIView):
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    permission_classes = [permissions.AllowAny]
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        # Extract data from the request
        job_number = request.data.get('job_number', None)
        project_name = request.data.get('project_name', None)
        po_date = request.data.get('po_date', None)
        project_status = request.data.get('project_status', None)
        client_id = request.data.get('client', None)

        # Extract file data in the desired format
        file_titles = [request.data.get(f'title{i}', None) for i in range(1, 100)]  # Assuming a maximum of 100 files
        files_data = [request.FILES.get(f'file{i}', None) for i in range(1, 100)]

        # Filter out None values, assuming not all 100 files are provided
        file_titles = [title for title in file_titles if title is not None]
        files_data = [file_data for file_data in files_data if file_data is not None]

        # Validate that required fields are present
        if not all([job_number, project_name, po_date, project_status, client_id, file_titles, files_data]):
            return Response({'error': 'Incomplete data provided'}, status=status.HTTP_400_BAD_REQUEST)

        # Validate that the number of files matches the number of file titles
        if len(file_titles) != len(files_data):
            return Response({'error': 'Number of file titles does not match the number of files'}, status=status.HTTP_400_BAD_REQUEST)

        # Validate the date format
        try:
            # Convert the date string to a datetime object in the expected format
            po_date = datetime.strptime(po_date, '%y-%m-%d').date()
        except ValueError:
            return Response({'error': 'Invalid date format'}, status=status.HTTP_400_BAD_REQUEST)

        # Get the Client instance based on the provided client_id
        try:
            client = Client.objects.get(pk=client_id)
        except Client.DoesNotExist:
            return Response({'error': 'Client does not exist'}, status=status.HTTP_400_BAD_REQUEST)

        # Create a new Job instance with the provided data
        job = Job.objects.create(
            job_number=job_number,
            project_name=project_name,
            po_date=po_date,
            project_status=project_status,
            client=client
        )

        # Handle files
        for title, file_data in zip(file_titles, files_data):
            File.objects.create(job=job, title=title, file=file_data)

        serializer = JobSerializer(job)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class JobDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    permission_classes = [permissions.AllowAny]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

    # Check if the query parameter 'delete_files_only' is set to 'true'
        delete_files_only = self.request.query_params.get('delete_files_only', False)
        print(f"Delete files only: {delete_files_only}")

        if delete_files_only:
        # Delete only the files associated with the job
            files_before = instance.file.all()
            print(f"Files before deletion: {files_before}")

            for file in files_before:
                print(f"File path to delete: {file.file.path}")
                file.file.delete()  # Delete the file from the storage
                file.delete()  # Delete the file instance

        # Update the job instance to remove the association with files
            instance.file.clear()
            instance.save()

            files_after = instance.file.all()
            print(f"Files after deletion: {files_after}")

            return Response(status=status.HTTP_204_NO_CONTENT)
        else:

            # Delete the job instance along with its files
            files = instance.file.all()
            for file in files:
                file.file.delete()  # Delete the file from the storage
                file.delete()  # Delete the file instance

            instance.delete()

            return Response(status=status.HTTP_204_NO_CONTENT)


#update method for job and file instance
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        # Update job details
        instance.job_number = request.data.get('job_number', instance.job_number)
        instance.project_name = request.data.get('project_name', instance.project_name)
        instance.po_date = request.data.get('po_date', instance.po_date)
        instance.project_status = request.data.get('project_status', instance.project_status)
        instance.client = Client.objects.get(pk=request.data.get('client', instance.client.pk))

        # Delete previous files associated with the job
        for file in instance.files.all():
            file.file.delete()
            file.delete()

        # Retrieve the new files from the request
        new_files_data = [request.FILES.get(f'file{i}', None) for i in range(1, 100)]
        new_file_titles = [request.data.get(f'title{i}', None) for i in range(1, 100)]

        # Filter out None values, assuming not all 100 files are provided
        new_files_data = [file_data for file_data in new_files_data if file_data is not None]
        new_file_titles = [title for title in new_file_titles if title is not None]

        # Create new files associated with the job
        for new_title, new_file_data in zip(new_file_titles, new_files_data):
            File.objects.create(job=instance, title=new_title, file=new_file_data)

        # Save the updated job instance
        instance.save()

        serializer = JobSerializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)