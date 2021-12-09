<template>
  <v-container>

    <v-row justify="center">
      <v-col cols="6">
        <v-row class="mt-8">
          <v-img
            :src="require('../assets/logo.svg')"
            class="my-3"
            contain
            height="200"
          />
        </v-row>

        <v-row class="mt-8">
          <v-file-input v-model="file" accept=".csv, text/csv" label="Elegí un archivo" outlined :show-size="1000"></v-file-input>
          <v-btn depressed color="primary" x-large class="ml-5" @click="upload()" :disabled="isLoading">
            Cargar
          </v-btn>
        </v-row>

        <v-progress-linear v-if="isLoading" :value="uploadPercentage"></v-progress-linear>

        <v-row class="mt-8">
          <v-expansion-panels accordion>
            <v-expansion-panel>
              <v-expansion-panel-header>
                <v-row>
                  <v-icon>mdi-cog</v-icon>
                  <div class="ml-5">Parámetros avanzados</div>
                </v-row>
              </v-expansion-panel-header>
              <v-expansion-panel-content>
                <v-text-field v-model="idField" label="Campo a usar como ID"></v-text-field>
                <v-text-field v-model="bodyField" label="Campo a usar como body"></v-text-field>
              </v-expansion-panel-content>
            </v-expansion-panel>
          </v-expansion-panels>
        </v-row>
      
      </v-col>
    </v-row>

    <v-snackbar v-model="showSnackbar">{{snackbarText}}</v-snackbar>

  </v-container>
</template>


<script>
  import axios from 'axios';

  export default {
    name: 'Upload',

    data: () => ({
      file: undefined, idField: 'uniq_id',
      bodyField: 'product_name', isLoading: false,
      uploadPercentage: 0, showSnackbar: false,
      snackbarText: ''
    }),

    methods: {
      async upload() {
        if(!this.file)
          return;

        const formData = new FormData();
        formData.append('file', this.file);

        if(this.idField)
          formData.append('id_field', this.idField)

        if(this.bodyField)
          formData.append('body_field', this.bodyField)
        
        this.isLoading = true;
        
        try {
          await axios.post('http://localhost:5000/api/data', formData, {
            headers: {
              'Content-Type': 'multipart/form-data'
            },
            onUploadProgress: function( progressEvent ) {
              this.uploadPercentage = parseInt( Math.round( ( progressEvent.loaded / progressEvent.total ) * 100 ) );
            }.bind(this)
          });
        } catch(e) {
          this.snackbarText = 'Ups! Ha ocurrido un error en la carga';
        }

        this.isLoading = false;
        this.snackbarText = 'Archivo cargado exitosamente!';
        this.showSnackbar = true;
      },
      open() {

      }
    }
  }
</script>
