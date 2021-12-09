<template>
  <v-container>

    <v-row justify="center">
      <v-col cols="6">
        <v-row class="mt-8">
          <v-img
            :src="require('../assets/logo_full.png')"
            class="my-3"
            contain
            height="150"
          />
        </v-row>

        <v-row class="mt-8">
          <v-text-field outlined prepend-inner-icon="mdi-search" v-on:keyup.enter="search()"
            v-model="queryStr" label="¿Qué deseas buscar?"></v-text-field>
          <v-btn depressed color="primary" x-large class="ml-5" @click="search()">
            Buscar
          </v-btn>
        </v-row>

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
                <v-switch v-model="useParentOf" label="Incluir subclases"></v-switch>

                <v-switch v-model="useClassOf" label="Incluir instancias"></v-switch>

                <v-subheader>Profundidad de búsqueda</v-subheader>
                <v-slider v-model="depth" step="1" thumb-label ticks :max="5"></v-slider>
              </v-expansion-panel-content>
            </v-expansion-panel>
          </v-expansion-panels>
        </v-row>
      
      </v-col>
    </v-row>

    <v-divider class="mt-16" v-if="searched"></v-divider>

    <v-row class="mt-8" justify="center">
      <v-progress-circular v-if="isLoading" indeterminate color="primary"></v-progress-circular>
    </v-row>

    <v-row class="mt-8" align="center" justify="center">

      <template v-if="searched && documents.length == 0">
        <h2>No se han encontrado resultados</h2>
      </template>

      <template v-else>
        <v-col cols="12" sm="3" md="4" v-for="doc in documents" :key="doc.id">
          <v-card class="mt-8 ml-8" elevation="2">
            <!-- <v-card-title>{{doc.id}}</v-card-title> -->

            <v-card-text>
              {{doc.description}}

              <v-chip-group column class="mt-3">
                  <v-chip v-for="label in doc.labels" :key="label">{{label}}</v-chip>
              </v-chip-group>
            </v-card-text>

            <v-card-actions>
              <v-btn text @click="open(doc)" color="primary">
                VER
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-col>
      </template>

    </v-row>

  </v-container>
</template>


<script>
  import axios from 'axios';

  export default {
    name: 'Home',

    data: () => ({
      queryStr: '', useParentOf: true, useClassOf: true, depth: 2,
      documents: [],
      isLoading: false,
      searched: false,
    }),

    methods: {
      async search() {
        if(this.queryStr == '' || !(this.useParentOf || this.useClassOf)) {
          this.searched = false
          this.documents = []
          return;
        }
        
        this.isLoading = true;
        const res = await axios.get('http://localhost:5000/api/search', {
          params: {
            query: this.queryStr, useParentOf: this.useParentOf ? 1 : 0,
            useClassOf: this.useClassOf ? 1 : 0, depth: this.depth
          }
        });

        this.searched = true;
        this.documents = res.data.docs

        this.documents = this.documents.map(d => { return {id: d.id, labels: d.labels, description: d.description.substr(0,200)} })

        this.isLoading = false;
      },
      open() {

      }
    }
  }
</script>
